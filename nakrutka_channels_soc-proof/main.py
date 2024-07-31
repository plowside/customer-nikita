# -*- coding: UTF-8 -*-
import traceback, sqlite3, logging, asyncio, httpx, socks, time, random, copy

from config import *
from tg_bot import main as tg_bot_func

##############################################################################
logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s', level=logging.INFO)
logging.getLogger('aiogram').setLevel(logging.WARNING)
logging.getLogger('httpx').setLevel(logging.WARNING)

version = 1.0
##############################################################################
con = sqlite3.connect('db.db')
cur = con.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS channels(
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	channel_id INTEGER
)''')
cur.execute('''CREATE TABLE IF NOT EXISTS channels_tasks(
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	channeld_id INTEGER,
	task_type TEXT,
	task_link TEXT,
	status INTEGER DEFAULT 0
)''')
cur.execute('''CREATE TABLE IF NOT EXISTS channels_actions(
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	channel_task_id INTEGER,
	action_id INTEGER,
	action_time_before_start INTEGER,
	action_count INTEGER,
	soc_proof_order_id INTEGER,
	unix INTEGER
)''')



async def check_version():
	try:
		async with httpx.AsyncClient() as client:
			resp = (await client.get('https://customer-nikita.vercel.app')).json()
			if version != resp['nakrutka_subscribers_soc-proof']:
				logging.warning(f'\n\n\nДоступна новая версия скрипта: {resp["nakrutka_subscribers_soc-proof"]} | Скачать: https://github.com/plowside/customer-nikita\n\n\n')
	except:
		...

class session_manager:
	def __init__(self, targets):
		self.targets = targets

	
	# Проверка целей (каналов)
	async def init_targets(self):
		targets = dict(self.targets)
		self.targets = []
		active = []
		db_channels = [channel[1] for channel in cur.execute('SELECT * FROM channels').fetchall()]

		for channel_id in targets:
			if channel_id not in self.targets:
				self.targets.append(channel_id)
			if channel_id not in db_channels:
				cur.execute('INSERT INTO channels(channel_id) VALUES (?)', [channel_id])
				channel_data = cur.execute('SELECT * FROM channels WHERE channel_id = ?', [channel_id]).fetchone()
				cur.execute('INSERT INTO channels_tasks(channeld_id, task_type, task_link) VALUES (?, ?, ?)', [channel_data[0], 'channel', target_channels[channel_id]])
				active.append(channel_id)
			else:
				channel_data = cur.execute('SELECT * FROM channels WHERE channel_id = ?', [channel_id]).fetchone()
				active_tasks = [x for x in cur.execute('SELECT * FROM channels_tasks WHERE channeld_id = ?', [channel_data[0]]).fetchall() if x[4] == 0]
				if len(active_tasks) == 0: logging.info(f'Все задачи для канала {channel_id} выполнены')
				else: active.append(channel_id)
		con.commit()
		self.channels = {x[1]: x[0] for x in cur.execute('SELECT * FROM channels').fetchall()}
		print('\n\n')
		logging.info(f'Активных задач: {len(active)}')

	async def channels_watcher(self):
		last_story = time.time()
		while True:
			try:
				channels = copy.deepcopy(self.channels)
				for (channel_id, channeld_id) in channels.items():
					zxc = copy.deepcopy(target_channels_strategy)
					channel_tasks = cur.execute('SELECT * FROM channels_tasks WHERE channeld_id = ? AND status == 0', [channeld_id]).fetchall()
					for channel_task in channel_tasks:
						soc_proof_service = soc_proof_services.get(channel_task[2])
						if not soc_proof_service or not soc_proof_service['enabled']:
							continue
						soc_proof_service_id = soc_proof_service['service_id']
						soc_proof_service = zxc[channel_id][channel_task[2]]
						task_link = channel_task[3]
						channel_task_id = channel_task[0]
						channel_completed_actions = cur.execute('SELECT * FROM channels_actions WHERE channel_task_id = ? ORDER BY unix ASC', [channel_task_id]).fetchall()
						channel_completed_actions_ids = [x[2] for x in channel_completed_actions]
						if len(channel_completed_actions) == 0: last_action_unix = 0
						else: last_action_unix = channel_completed_actions[-1][-1]

						channel_actions = [(i, x) for i, x in enumerate(soc_proof_service['strategy']) if i not in channel_completed_actions_ids]
						if len(channel_actions) == 0:
							cur.execute('UPDATE channels_tasks SET status = 1 WHERE id = ?', [channel_task_id])
							con.commit()
							logging.info(f'[{channel_id}] Накрутка завершена')
							continue
						channel_action_id, channel_action = channel_actions[0]
						channel_action['time_before_start'] = random.randint(*channel_action['time_before_start'])
						channel_action['count'] = random.randint(*channel_action['count'])
						if time.time() - last_action_unix < channel_action['time_before_start']:
							continue
						async with httpx.AsyncClient(timeout=180) as hclient:
							resp = (await hclient.post('https://partner.soc-proof.su/api/v2', json={'key': soc_proof_api_token, 'action': 'add', 'service': soc_proof_service_id, 'quantity': channel_action['count'], 'link': task_link})).json()
						
						errors_text = {
							"neworder.error.not_enough_funds": "❗️❗️ Недостаточно средств на балансе панели ❗️❗️", 
							"error.incorrect_service_id": "Данная услуга больше не предоставляется, либо перенесена в другой раздел, попробуйте начать сначала.",
							"neworder.error.link": "Указана недействительная ссылка.",
							"neworder.error.min_quantity": "Минимальное кол-во указано в описании услуги.",
							"neworder.error.max_quantity": "Максимальное кол-во указано в описании услуги."
						}

						if 'error' in resp:
							if resp.get('error') == 'neworder.error.not_enough_funds':
								async with httpx.AsyncClient(timeout=180) as hclient:
									await hclient.get(f'https://api.telegram.org/bot{bot_token}/sendMessage', params={'chat_id': log_chat_id, 'text': f'<b>❗️❗️ Недостаточно средств на балансе панели ❗️❗️</b>', 'parse_mode': 'HTML', 'disable_web_page_preview': True})
							error = errors_text.get(resp.get('error'))
							if not error: error = resp.get('error')
							elif error == 'neworder.error.link_duplicate': continue
							logging.warning(f'[{channel_id}|{channel_action_id}] Не удалось создать накрутку: {error}')
							continue
						
						order_id = resp['order']
						if not order_id:
							logging.warning(f'[{channel_id}|{channel_action_id}] Не удалось создать накрутку: {resp}')
							continue
						cur.execute('INSERT INTO channels_actions(channel_task_id, action_id, action_time_before_start, action_count, soc_proof_order_id, unix) VALUES (?, ?, ?, ?, ?, ?)', [channel_task_id, channel_action_id, channel_action['time_before_start'], channel_action['count'], order_id, int(time.time())])
						logging.info(f'[{channel_id}|{channel_action_id}] Накрутка запущена')
						async with httpx.AsyncClient(timeout=180) as hclient:
							await hclient.get(f'https://api.telegram.org/bot{bot_token}/sendMessage', params={'chat_id': log_chat_id, 'text': f'<b>✅ Накрутка запущена</b>\n├ ID канала: <code>{channel_id}</code>\n├ ID стратегии накрутки: <code>{channel_action_id}</code>\n├ Ссылка на цель: <b>{task_link}</b>\n└ Данные стратегии накрутки: <b>{channel_action}</b>', 'parse_mode': 'HTML', 'disable_web_page_preview': True})
						if len(channel_actions) == 1:
							cur.execute('UPDATE channels_tasks SET status = 1 WHERE id = ?', [channel_task_id])
							con.commit()
							logging.info(f'[{channel_id}] Накрутка завершена')
			except Exception as e:
				logging.error(f'[LINE:{traceback.extract_tb(e.__traceback__)[-1].lineno}] Во время поиска новых задач произошла ошибка: {e}')
			await asyncio.sleep(10)


async def main():
	await check_version()
	future = asyncio.create_task(tg_bot_func(soc_proof_services))
	client = session_manager(target_channels)

	await client.init_targets()
	if len(client.targets) == 0:
		logging.info('Нет целей для работы')
		exit()

	logging.info('Скрипт запущен')
	await client.channels_watcher()

if __name__ == '__main__':
	asyncio.run(main())