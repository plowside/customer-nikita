# -*- coding: UTF-8 -*-
import telethon, logging, asyncio, sqlite3, httpx, time

from telethon import TelegramClient, functions, events, types
from telethon.tl.functions.messages import GetHistoryRequest, ImportChatInviteRequest, CheckChatInviteRequest, GetPeerDialogsRequest
from telethon.tl.functions.channels import JoinChannelRequest, LeaveChannelRequest
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.errors import rpcerrorlist

from config import *

##############################################################################
logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s', level=logging.INFO)
logging.getLogger('telethon').setLevel(logging.WARNING)
logging.getLogger('httpx').setLevel(logging.WARNING)
##############################################################################
con = sqlite3.connect('db.db')
cur = con.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS channels(
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	channel_id INTEGER,
	user_id INTEGER
)''')
cur.execute('''CREATE TABLE IF NOT EXISTS channels_tasks(
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	channeld_id INTEGER,
	message_id INTEGER,
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
			resp = (await client.get('https://api.jsonsilo.com/e07e7a79-a12a-4afb-bca8-3845488ac653', headers={'X-SILO-KEY': 'v7OtokI8fNdHZctKJ43Jjyn4CwFkLafu5wft3KGW9e'})).json()
			if version != resp['boost_posts_stories_soc-proof']:
				logging.warning(f'\n\n\nДоступна новая версия скрипта: {resp["boost_posts_stories_soc-proof"]} | Скачать: https://github.com/plowside/customer-nikita\n\n\n')
	except:
		...

class session_manager:
	def __init__(self, session_path, targets):
		self.targets = targets
		self.session_path = session_path
		self.channels_usernames = {}
		self.channels_stories = {}

	# Подключение к сессии
	async def init_session(self):
		self.client = TelegramClient(self.session_path, 69696969, 'qwertyuiopasdfghjklzxcvbnm1234567', flood_sleep_threshold=120, device_model = "iPhone 13 Pro Max", system_version = "14.8.1", app_version = "10.6", lang_code = "en", system_lang_code = "en-US")
		
		try: await self.client.connect()
		except ConnectionError:	
			await self.client.disconnect()
			logging.info(f'Ошибка подключения к сессии')
			return False
		except rpcerrorlist.FloodWaitError: 
			await self.client.disconnect()
			logging.info(f'Лимит авторизаций')
			return False
		except:
			await self.client.disconnect()
			logging.info(f'Неизвестная ошибка аккаунта')
			return False
		if not await self.client.is_user_authorized(): 
			await self.client.disconnect()
			logging.info(f'Мертвая сессия')
			return False

		await self.client.start()
		me = await self.client.get_me()
		self.me = me
		logging.info(f'Успешно подключился к сессии')

		await self.init_handlers()
		return True


	async def init_handlers(self):
		self.client.add_event_handler(self.on_new_message, events.NewMessage(chats=self.targets))
	
	# Проверка целей (каналов)
	async def init_targets(self):
		targets = dict(self.targets)
		self.targets = []
		logging.info(f'Проверяю каналы: {len(targets)} шт.')
		user_channels = [dialog.id for dialog in await self.client.get_dialogs() if dialog.is_group or dialog.is_channel]
		db_channels = [channel[1] for channel in cur.execute('SELECT * FROM channels WHERE user_id = ?', [self.me.id]).fetchall()]

		for channel_id in targets:
			if channel_id not in user_channels:
				try:
					try: await self.client(JoinChannelRequest(targets[channel_id].replace('+', '').replace('https://t.me/', '')))
					except: await self.client(ImportChatInviteRequest(targets[channel_id].replace('+', '').replace('https://t.me/', '')))
				except rpcerrorlist.InviteRequestSentError:
					logging.info(f'[{channel_id}] Отправил запрос на вступление в канал')
					continue
				except rpcerrorlist.InviteHashExpiredError:
					logging.info(f'[{channel_id}] Пригласительная ссылка устарела')
					continue
				except rpcerrorlist.UserAlreadyParticipantError:
					...
				except Exception as e:
					logging.info(f'[{channel_id}] Не удалось присоединиться к каналу: {e}')
					continue

			channel = await self.client.get_entity(channel_id)
			if channel_id not in self.channels_usernames:
				self.channels_usernames[channel_id] = channel.username

			if channel_id == -1002103652482: continue
			for story in (await self.client(functions.stories.GetPeerStoriesRequest(peer=channel_id))).stories.stories:
				if channel_id in self.channels_stories:
					self.channels_stories[channel_id].append(story.id)
				else:
					self.channels_stories[channel_id] = [story.id]


			if channel_id not in self.targets:
				self.targets.append(channel_id)

			if channel_id not in db_channels:
				cur.execute('INSERT INTO channels(channel_id, user_id) VALUES (?, ?)', [channel_id, self.me.id])

		con.commit()
		self.channels = {x[1]: x[0] for x in cur.execute('SELECT * FROM channels WHERE user_id = ?', [self.me.id]).fetchall()}
		logging.info(f'Успешно проверенных каналов: {len(targets)} шт.')



	# Хендлер на Новый пост в канале
	async def on_new_message(self, event):
		channel_id = event.message.peer_id.channel_id
		message_id = event.id
		if channel_id in self.channels_usernames:
			channel_username = self.channels_usernames[channel_id]
		else:
			channel_username = (await event.get_chat()).username
			self.channels_usernames[channel_id] = channel_username
		message_link = f'https://t.me/{channel_username}/{message_id}'
		if not str(channel_id).startswith('-100'): channel_id = int(f'-100{channel_id}')
		channeld_id = self.channels.get(channel_id)
		if not channeld_id:
			logging.error(f'[{channel_id}] Не удалось найти канал в базе данных')
			return
		task_type = 'post'
		cur.execute('INSERT INTO channels_tasks(channeld_id, message_id, task_type, task_link) VALUES (?, ?, ?, ?)', [channeld_id, message_id, task_type, message_link])
		con.commit()
		logging.info(f'[{channel_id}] Новая задача: {message_id}|{task_type}')

	async def channels_watcher(self):
		last_story = time.time()
		while True:
			try:
				channels = dict(self.channels)
				if time.time() - last_story > 300:
					for (channel_id, channeld_id) in channels.items():
						db_stories = [x[2] for x in cur.execute('SELECT * FROM channels_tasks WHERE channeld_id = ? AND task_type = ?', [channeld_id, 'story']).fetchall()]
						for story in (await self.client(functions.stories.GetPeerStoriesRequest(peer=channel_id))).stories.stories:
							new = False
							if channel_id in self.channels_stories:
								if story.id not in self.channels_stories[channel_id]:
									self.channels_stories[channel_id].append(story.id)
									new = True
							else:
								self.channels_stories[channel_id] = [story.id]
								new = True
							if story.id in db_stories or not new: continue
							story_link = f'https://t.me/{self.channels_usernames[channel_id]}/s/{story.id}'
							cur.execute('INSERT INTO channels_tasks(channeld_id, message_id, task_type, task_link) VALUES(?, ?, ?, ?)', [channeld_id, story.id, 'story', story_link])
							con.commit()
							logging.info(f'[{channel_id}] Новая задача: {story.id}|story')
						await asyncio.sleep(3)
					last_story = time.time()

				# Проверка конфига на изменения
				try:
					with open('config.py', 'r', encoding='utf-8') as file:
						config_content = file.read()
					start_index = config_content.find('soc_proof_services = {')
					end_index = config_content.find('}#', start_index) + 1
					soc_proof_services_str = config_content[start_index:end_index]
					temp = eval(soc_proof_services_str[soc_proof_services_str.find('=') + 1:].strip())
					if temp != soc_proof_services:
						logging.info(f'Изменение в конфиге: {temp}')
					for x in soc_proof_services:
						soc_proof_services[x] = temp[x]
				except Exception as e:
					logging.error(f'Не удалось проверить конфиг: {e}')
				for (channel_id, channeld_id) in channels.items():
					channel_tasks = cur.execute('SELECT * FROM channels_tasks WHERE channeld_id = ? AND status in (0, 1)', [channeld_id]).fetchall()
					for channel_task in channel_tasks:
						soc_proof_service = soc_proof_services.get(channel_task[3])
						if not soc_proof_service or not soc_proof_service['enabled']:
							continue
						soc_proof_service_id = soc_proof_service['service_id']
						soc_proof_service = target_channels_strategy[channel_id][channel_task[3]]
						message_id = channel_task[2]
						task_link = channel_task[4]
						channel_task_id = channel_task[0]
						channel_completed_actions = cur.execute('SELECT * FROM channels_actions WHERE channel_task_id = ? ORDER BY unix ASC', [channel_task_id]).fetchall()
						channel_completed_actions_ids = [x[2] for x in channel_completed_actions]
						if len(channel_completed_actions) == 0:
							last_action_unix = 0
						else:
							last_action_unix = channel_completed_actions[-1][-1]

						channel_actions = [(i, x) for i, x in enumerate(soc_proof_service['strategy']) if i not in channel_completed_actions_ids]
						if len(channel_actions) == 0:
							cur.execute('UPDATE channels_tasks SET status = 1 WHERE id = ?', [channel_task_id])
							logging.info(f'[{channel_id}|{message_id}|{channel_action_id}] Накрутка завершена')
						channel_action_id, channel_action = channel_actions[0]
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
							logging.warning(f'[{channel_id}|{message_id}|{channel_action_id}] Не удалось создать накрутку: {error}')
							continue
						
						order_id = resp['order']
						if not order_id:
							logging.warning(f'[{channel_id}|{message_id}|{channel_action_id}] Не удалось создать накрутку: {resp}')
							continue
						cur.execute('INSERT INTO channels_actions(channel_task_id, action_id, action_time_before_start, action_count, soc_proof_order_id, unix) VALUES (?, ?, ?, ?, ?, ?)', [channel_task_id, channel_action_id, channel_action['time_before_start'], soc_proof_service_id, order_id, int(time.time())])
						logging.info(f'[{channel_id}|{message_id}|{channel_action_id}] Накрутка запущена')
						async with httpx.AsyncClient(timeout=180) as hclient:
							await hclient.get(f'https://api.telegram.org/bot{bot_token}/sendMessage', params={'chat_id': log_chat_id, 'text': f'<b>✅ Накрутка запущена</b>\n├ ID канала: <code>{channel_id}</code>\n├ ID стратегии накрутки: <code>{channel_action_id}</code>\n├ Ссылка на цель: <b>{task_link}</b>\n└ Данные стратегии накрутки: <b>{channel_action}</b>', 'parse_mode': 'HTML', 'disable_web_page_preview': True})
						if len(channel_actions) == 1:
							cur.execute('UPDATE channels_tasks SET status = 1 WHERE id = ?', [channel_task_id])
							logging.info(f'[{channel_id}|{message_id}|{channel_action_id}] Накрутка завершена')
					con.commit()
				await asyncio.sleep(10)

			except rpcerrorlist.FloodWaitError:
				logging.error(f'Во время поиска новых задач произошла ошибка: {e}')
				await asyncio.sleep(30)
			except Exception as e:
				logging.error(f'Во время поиска новых задач произошла ошибка: {e}')



async def main():
	await check_version()
	client = session_manager(session, target_channels)
	status = await client.init_session()
	if not status:
		exit()

	await client.init_targets()
	if len(client.targets) == 0:
		logging.info('Нет целей для работы')
		exit()

	await client.channels_watcher()

if __name__ == '__main__':
	asyncio.run(main())