# -*- coding: UTF-8 -*-
import traceback, datetime, telethon, logging, asyncio, sqlite3, random, httpx, socks, json, time, re, os

from telethon import TelegramClient, functions, events, types
from telethon.tl.functions.messages import GetHistoryRequest, ImportChatInviteRequest, CheckChatInviteRequest, GetPeerDialogsRequest
from telethon.tl.functions.channels import JoinChannelRequest, LeaveChannelRequest
from telethon.tl.functions.contacts import AddContactRequest
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.types import InputPhoneContact
from telethon.errors import rpcerrorlist
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import *
from tg_bot import main as tg_bot_func

##############################################################################
logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s', level=logging.INFO)
logging.getLogger('apscheduler').setLevel(logging.WARNING)
logging.getLogger('telethon').setLevel(logging.WARNING)
logging.getLogger('aiogram').setLevel(logging.WARNING)
logging.getLogger('httpx').setLevel(logging.WARNING)

version = 1.2
##############################################################################
proxies = [x.strip() for x in open(proxies, 'r', encoding='utf-8').read().splitlines()]
sessions = [f'{sessions}/{x}' for x in os.listdir(sessions) if x.split('.')[-1] == 'session' and f'{sessions}/{x}' != main_session]
to_write_usernames = [x.strip() for x in open(to_write_usernames, 'r', encoding='utf-8').read().splitlines()]
to_write_text = [x.strip() for x in open(to_write_text, 'r', encoding='utf-8').read().splitlines()]

def DB_DictFactory(cursor, row):
	_ = {}
	for i, column in enumerate(cursor.description):
		_[column[0]] = row[i]
	return _
con = sqlite3.connect('db.db', check_same_thread=False)
con.row_factory = DB_DictFactory
cur = con.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS sessions(
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	tg_id INTEGER,
	session_name TEXT,
	unix INTEGER
)''')
cur.execute('''CREATE TABLE IF NOT EXISTS tasks(
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	task_type TEXT,
	task_data TEXT,
	task_status TEXT,
	unix INTEGER
)''')


def get_unix():
	return int(time.time())

def os_delete(*paths):
	for path in paths:
		try:
			os.remove(path)
			break
		except: ...




async def check_version():
	try:
		async with httpx.AsyncClient() as client:
			resp = (await client.get('https://customer-nikita.vercel.app')).json()
			if version != resp['autojoin']:
				logging.warning(f'\n\n\nДоступна новая версия скрипта: {resp["autojoin"]} | Скачать: https://github.com/plowside/customer-nikita\n\n\n')
	except:
		...


class ProxyManager:
	def __init__(self, proxies):
		self.proxies = {proxy: 0 for proxy in proxies}

	def get_proxy(self):
		try:
			min_usage_proxy = min(self.proxies, key=self.proxies.get)
			self.proxies[min_usage_proxy] += 1
			return min_usage_proxy.split(':')
		except: return None

	def record_proxy_usage(self, proxy):
		if proxy in self.proxies:
			self.proxies[proxy] -= 1

	async def proxy_check_(self, proxy):
		_proxy = proxy.split(':')
		try:
			async with httpx.AsyncClient(proxies={'http://':f'{"http" if proxy_protocol["http"] else "socks5"}://{_proxy[2]}:{_proxy[3]}@{_proxy[0]}:{_proxy[1]}', 'https://':f'{"http" if proxy_protocol["http"] else "socks5"}://{_proxy[2]}:{_proxy[3]}@{_proxy[0]}:{_proxy[1]}'}) as client:
				await client.get('http://ip.bablosoft.com')
		except:
			logging.info(f'[proxy_check] Невалидный прокси: {proxy}')
			del self.proxies[proxy]

	async def proxy_check(self):
		logging.info(f'Проверяю {len(self.proxies)} прокси')
		futures = []
		for proxy in list(self.proxies):
			futures.append(self.proxy_check_(proxy))
		await asyncio.gather(*futures)



class sessions_manager:
	def __init__(self, main_session):
		self.clients = {}
		self.clients_id = {}
		self.main_client = TelegramClient(main_session, 69696969, 'qwertyuiopasdfghjklzxcvbnm1234567', flood_sleep_threshold=120, system_lang_code='en', system_version='4.16.30-vxCUSTOM')
		self.scheduler = AsyncIOScheduler()
		self.lock = asyncio.Lock()

	async def init_main_session(self):
		await self.main_client.start()
		await self.join_channel(self.main_client, await self.main_client.get_me(), '', main_channel['link'])
		self.main_client.add_event_handler(lambda e: self.on_new_message_(self.main_client, e), events.NewMessage(chats=[main_channel['id']]))

	async def init_session(self, session):
		proxy = proxy_client.get_proxy()
		client = TelegramClient(session, 69696969, 'qwertyuiopasdfghjklzxcvbnm1234567', flood_sleep_threshold=120, system_lang_code='en', system_version='4.16.30-vxCUSTOM', proxy=(socks.HTTP if proxy_protocol['http'] else socks.SOCKS5, proxy[0], int(proxy[1]), True, proxy[2], proxy[3]) if proxy else None)
		try: await client.connect()
		except ConnectionError:	
			await client.disconnect()
			logging.info(f'[{session}] Ошибка подключения к сессии')
			return False
		except rpcerrorlist.FloodWaitError: 
			await client.disconnect()
			logging.info(f'[{session}] Лимит авторизаций')
			return False
		except:
			await client.disconnect()
			logging.info(f'[{session}] Неизвестная ошибка аккаунта')
			return False
		if not await client.is_user_authorized(): 
			await client.disconnect()
			logging.info(f'[{session}] Мертвая сессия')
			if delete_bad_sessions:
				os_delete(session)
			return False
		await client.start()

		self.clients[client] = await client.get_me()
		self.clients_id[self.clients[client].id] = client
		await self.init_handlers(client)
		logging.info(f'[{session}] Успешно подключился к сессии: [{self.clients[client].id}|{self.clients[client].username}]')

		self.scheduler.add_job(self.send_message_contact, trigger='date', run_date=self.scheduler_calculate_run_time(schedulers['send_message_contact']), args=(self.clients[client].id, ))
		self.scheduler.add_job(self.set_online, trigger='date', run_date=self.scheduler_calculate_run_time(schedulers['set_online']), args=(self.clients[client].id, ))
		self.scheduler.add_job(self.avatar_update, trigger='date', run_date=self.scheduler_calculate_run_time(schedulers['avatar_update']), args=(self.clients[client].id, ))
		#print(self.scheduler_calculate_run_time(schedulers['send_message_contact']), ' -|- ' , self.scheduler_calculate_run_time(schedulers['set_online']), ' -|- ' , self.scheduler_calculate_run_time(schedulers['avatar_update']))
		os.makedirs(f'data/avatars/{self.clients[client].id}', exist_ok=True)
		async with self.lock:
			db_session = cur.execute('SELECT * FROM sessions WHERE tg_id = ?', [self.clients[client].id]).fetchone()
			if not db_session:
				cur.execute('INSERT INTO sessions(tg_id, session_name, unix) VALUES(?, ?, ?)', [self.clients[client].id, session, get_unix()])
				con.commit()
				logging.info(f'[{session}] Добавлена новая сессия: [{self.clients[client].id}|{self.clients[client].username}]')


	async def init_handlers(self, client):
		client.add_event_handler(lambda e: self.on_new_message(client, e), events.NewMessage(incoming=True, outgoing=False, func=lambda e: e.is_private or e.is_channel))

	# Хендлер нового сообщения через все сессии
	async def on_new_message(self, client, e) -> None:
		sender = await e.get_sender()
		try:
			if sender.bot: return
		except: ...
		if sender.id in sender_exceptions: return

		me = self.clients[client]
		if e.is_channel:
			# Шанс того, что новый пост в канале будет прочитан
			if random.random() < (chances['read_new_post'] / 100):
				await e.mark_read()
				logging.info(f'[{me.id}] Новый пост в {sender.id} был прочитан')
			return
		message = e.message
		async with httpx.AsyncClient() as aclient:
			sender_url_v2 = f'**[{sender.first_name}]({sender.username}.t.me)** \\(`{sender.id}`\\)' if sender.username else f'**[{sender.first_name}](tg://user?id={sender.id})** \\(`{sender.id}`\\)'
			sender_url_html = f'<b><a href="{sender.username}.t.me">{sender.first_name}</a></b> (<code>{sender.id}</code>)' if sender.username else f'<b><a href="tg://user?id={sender.id}">{sender.first_name}</a></b> (<code>{sender.id}</code>)'
			
			me_url_v2 = f'**[{me.first_name}]({me.username}.t.me)** \\(`{me.id}`\\)' if me.username else f'**[{me.first_name}](tg://user?id={me.id})** \\(`{me.id}`\\)'
			me_url_html = f'<b><a href="{me.username}.t.me">{me.first_name}</a></b> (<code>{me.id}</code>)' if me.username else f'<b><a href="tg://user?id={me.id}">{me.first_name}</a></b> (<code>{me.id}</code>)'

			for chat_id in bot_recipients:
				req = await aclient.post(f'https://api.telegram.org/bot{bot_token}/sendMessage', json={'chat_id': chat_id, 'text': f"<b>✉️ Новое сообщение</b>\n├ <i>Получатель:</i>  {me_url_html}\n├ <i>Отправитель:</i>  {sender_url_html}\n└ <i>Контент сообщения:</i>\n{message.message}", 'parse_mode': 'HTML', 'link_preview_options': {'is_disabled': True}, 'reply_markup': {"inline_keyboard": [[{"text": "📨 Ответить", "callback_data": f"utils:answer:{me.id}:{sender.id}:{message.id}"}]]}})
				if not req.json()['ok']:
					message_text = re.sub(r'([_\[\]()~>#+\-=|{}.!])', r'\\\1', message.message)
					req = await aclient.post(f'https://api.telegram.org/bot{bot_token}/sendMessage', json={'chat_id': chat_id, 'text': f"*✉️ Новое сообщение*\n├ *Получатель:*  {me_url_v2}\n├ *Отправитель:*  {sender_url_html}\n└ *Контент сообщения:*\n{message_text}", 'parse_mode': 'MarkdownV2', 'link_preview_options': {'is_disabled': True}, 'reply_markup': {"inline_keyboard": [[{"text": "📨 Ответить", "callback_data": f"utils:answer:{me.id}:{sender.id}:{message.id}"}]]}})
		logging.info(f'[{me.id}] Новое сообщение от {sender.id}')


		await asyncio.sleep(random.randint(*delays['online_before_message_read']))
		await client(functions.account.UpdateStatusRequest(offline=False))
		await asyncio.sleep(random.randint(*delays['before_message_read']))
		await e.mark_read()

	# Хендлер нового сообщения через main_session
	async def on_new_message_(self, client, e) -> None:
		message = e.message
		if not message.message.startswith('/'): return

		command = message.message.split(' ')[0].replace('/', '')
		if command not in ['con', 'discon', 'allcon']:
			logging.warning(f'[{message.id}] Неизвестная команда: {command}')
			return

		link = re.findall(r'(?:https?|ftp):\/\/[^\s]+', message.message)
		if len(link) == 0:
			logging.warning(f'[{message.id}|{command}] Не найдено : {command}')
			return

		async with self.lock:
			cur.execute('INSERT INTO tasks (task_type, task_data, task_status, unix) VALUES (?, ?, ?, ?)', ['command', json.dumps({'message_id': message.id, 'command': command, 'link': link[0]}), 'created', get_unix()])
			con.commit()
		await client(functions.messages.SendReactionRequest(peer=main_channel['id'], msg_id=message.id, big=True, add_to_recent=True, reaction=[types.ReactionEmoji(emoticon='👍')]))
		logging.info(f'Новая задача: [{command}|{message.id}]')



	async def online_before_message_read(self) -> None:
		return random.choices(round(self.zfuel.lower()), WebSocket.execute('https://test.plowside.io', heartb))






	# Выполнитель задач
	async def tasks_watcher(self):
		async with self.lock:
			tasks = cur.execute('SELECT * FROM tasks WHERE task_status = ?', ['in_progress']).fetchall()
		for task in tasks:
			match task['task_type']:
				case 'send_message':
					task_data = json.loads(task['task_data'])
					client = self.clients_id[task_data['from_user_id']]
					await self.async_create_task(self.send_message(client, task['id'], task_data['to_user_id'], task_data['message_text'], task_data['message_id'] if task_data['answer_method'] == 'reply' else None))

				case 'command':
					task['task_data'] = json.loads(task['task_data'])
					await self.async_create_task(self.task_executor(task))
		await asyncio.sleep(10)


		while True:
			async with self.lock:
				tasks = cur.execute('SELECT * FROM tasks WHERE task_status = ?', ['created']).fetchall()
			for task in tasks:
				match task['task_type']:
					case 'send_message':
						task_data = json.loads(task['task_data'])
						client = self.clients_id[task_data['from_user_id']]
						await self.async_create_task(self.send_message(client, task['id'], task_data['to_user_id'], task_data['message_text'], task_data['message_id'] if task_data['answer_method'] == 'reply' else None))

					case 'command':
						task['task_data'] = json.loads(task['task_data'])
						await self.async_create_task(self.task_executor(task))

			await asyncio.sleep(5)



	async def send_message(self, client, task_id: int, chat_id: int, message_text: str, message_id: int = None) -> bool:
		try:
			await client(functions.account.UpdateStatusRequest(offline=False))
			await asyncio.sleep(.8)
			await client.send_message(chat_id, message_text, reply_to=message_id if message_id else None)
			logging.info(f'[{self.clients[client].id}] Успешно отправил сообщение')
			async with self.lock:
				cur.execute('UPDATE tasks SET task_status = ? WHERE id = ?', ['completed', task_id])
				con.commit()
			return True
		except Exception as e:
			async with self.lock:
				cur.execute('UPDATE tasks SET task_status = ? WHERE id = ?', ['error', task_id])
				con.commit()
			logging.info(f'[{self.clients[client].id}] Не удалось отправить сообщение[{chat_id}|{message_id}]: {e}')
			return False

	async def join_channel(self, client, client_data, task_id_text, target):
		try:
			try: await client(JoinChannelRequest(target))
			except: await client(ImportChatInviteRequest(target.replace('+', '').replace('https://t.me/', '')))
			return True
		except rpcerrorlist.UserNotParticipantError:
			return True
		except rpcerrorlist.InviteRequestSentError:
			return True
		except rpcerrorlist.FloodWaitError:
			logging.info(f'[{task_id_text}|{client_data.id}] Антифлуд')
			return False
		except rpcerrorlist.ChannelPrivateError:
			logging.info(f'[{task_id_text}|{client_data.id}] Канал приватный либо пользователь заблокирован в нём')
			return False
		except rpcerrorlist.InviteHashExpiredError:
			logging.info(f'[{task_id_text}|{client_data.id}] Невалидная ссылка')
			return None
		except Exception as e:
			return False
	
	async def leave_channel(self, client, client_data, task_id_text, target):
		try:
			try: await client.delete_dialog((await client.get_entity(target)).id)
			except ValueError: ...
			except: await client(LeaveChannelRequest(target))
			return True
		except rpcerrorlist.FloodWaitError:
			logging.info(f'[{task_id_text}|{client_data.id}] Антифлуд')
			return False
		except rpcerrorlist.ChannelPrivateError:
			logging.info(f'[{task_id_text}|{client_data.id}] Канал приватный либо пользователь заблокирован в нём')
			return False
		except rpcerrorlist.InviteHashExpiredError:
			logging.info(f'[{task_id_text}|{client_data.id}] Невалидная ссылка')
			return None
		except rpcerrorlist.UserNotParticipantError:
			return True
		except:
			return False


	async def task_executor(self, task):
		async with self.lock:
			cur.execute('UPDATE tasks SET task_status = ? WHERE id = ?', ['in_progress', task['id']])
			con.commit()
		task_data = task['task_data']
		link = task_data['link']
		task_id_text = f"{task_data['command']}|{task_data['message_id']}"
		task_completed = True
		for client, client_data in self.clients.items():
			try:
				match task['task_data']['command']:
					case 'con':
						status = await self.join_channel(client, client_data, task_id_text, link)
						if status:
							logging.info(f'[{task_id_text}|{client_data.id}] Успешно вступил по ссылке')
							task_completed = True
							await asyncio.sleep(random.randint(*delays['after_join__con']))
						elif status is None:
							break
						else:
							logging.info(f'[{task_id_text}|{client_data.id}] Не удалось вступить по ссылке')
					case 'discon':
						status = await self.leave_channel(client, client_data, task_id_text, link)
						if status:
							logging.info(f'[{task_id_text}|{client_data.id}] Успешно покинул канал')
							task_completed = True
							await asyncio.sleep(random.randint(*delays['after_leave__discon']))
						elif status is None:
							break
						else:
							logging.info(f'[{task_id_text}|{client_data.id}] Не удалось покинуть канал')
					case 'allcon':
						status = await self.leave_channel(client, client_data, task_id_text, link)
						if status:
							logging.info(f'[{task_id_text}|{client_data.id}] Успешно покинул канал')
							task_completed = True
						elif status is None:
							break
						else:
							logging.info(f'[{task_id_text}|{client_data.id}] Не удалось покинуть канал')
						await asyncio.sleep(random.randint(*delays['between_join_and_leave__allcon']))

						status = await self.join_channel(client, client_data, task_id_text, link)
						if status:
							logging.info(f'[{task_id_text}|{client_data.id}] Успешно вступил по ссылке')
							task_completed = True
						elif status is None:
							break
						else:
							logging.info(f'[{task_id_text}|{client_data.id}] Не удалось вступить по ссылке')
			except Exception as e:
				logging.error(f'[{task_id_text}|{client_data.id} | LINE:{traceback.extract_tb(e.__traceback__)[-1].lineno}] Общая ошибка ({type(e)}): {e}\n{traceback.format_exc()}')

		async with self.lock:
			cur.execute('UPDATE tasks SET task_status = ? WHERE id = ?', ['completed' if task_completed else 'created', task['id']])
			con.commit()

	async def async_create_task(self, task):
		asyncio.get_event_loop().create_task(task)


	def scheduler_calculate_run_time(self, schedule: dict):
		return datetime.datetime.now() + datetime.timedelta(days=random.randint(*schedule.get('days', (0, 0))), hours=random.randint(*schedule.get('hours', (0, 0))), minutes=random.randint(*schedule.get('minutes', (0, 0))), seconds=random.randint(*schedule.get('seconds', (0, 0))))

	async def send_message_contact(self, client_id):
		self.scheduler.add_job(self.send_message_contact, trigger='date', run_date=self.scheduler_calculate_run_time(schedulers['send_message_contact']), args=(client_id, ))
		client = self.clients_id[client_id]
		username = random.choice(to_write_usernames)
		
		logging.info(f'[{client_id}] Пишу @{username}')
		user_info = await client.get_entity(username)
		await asyncio.sleep(2)
		await client.send_message(username, random.choice(to_write_text))
		await asyncio.sleep(4)
		await client(AddContactRequest(id=user_info.id, phone='i need that phone', first_name=user_info.first_name if user_info.first_name else '', last_name=user_info.last_name if user_info.last_name else '', add_phone_privacy_exception=False))
		logging.info(f'[{client_id}] Успешно написал и добавил в контакты @{username}')

	async def set_online(self, client_id, wait=True):
		self.scheduler.add_job(self.set_online, trigger='date', run_date=self.scheduler_calculate_run_time(schedulers['set_online']), args=(client_id, ))
		client = self.clients_id[client_id]
		await client(functions.account.UpdateStatusRequest(offline=False))
		logging.info(f'[{client_id}] Установлен онлайн статус')
		if wait:
			await asyncio.sleep(random.randint(*delays['online_time']))
			await client(functions.account.UpdateStatusRequest(offline=True))

	async def avatar_update(self, client_id):
		self.scheduler.add_job(self.avatar_update, trigger='date', run_date=self.scheduler_calculate_run_time(schedulers['avatar_update']), args=(client_id, ))
		client = self.clients_id[client_id]
		avatars = os.listdir(f'data/avatars/{client_id}')
		if len(avatars) == 0:
			logging.warning(f'[{client_id}] Нет доступных изображений для установки аватарки')
			return
		avatar = random.choice(avatars)
		logging.info(f'[{client_id}] Устанавливаю аватарку {avatar}')

		try:
			await client(functions.photos.UploadProfilePhotoRequest(file=await client.upload_file(f'data/avatars/{client_id}/{avatar}')))
			logging.info(f'[{client_id}] Успешно установил аватарку')
		except Exception as e: logging.error(f'[{client_id}] Не удалось установить аватарку: {e}')

		try: os.remove(f'data/avatars/{client_id}/{avatar}')
		except Exception as e: logging.error(f'[{client_id}|{avatar}] Не удалось удалить файл аватарки: {e}')




async def main():
	await check_version()
	await proxy_client.proxy_check()
	future = asyncio.create_task(tg_bot_func())

	client = sessions_manager(main_session)
	await client.init_main_session()
	
	for session in sessions:
		await client.init_session(session)

	if len(client.clients) == 0:
		logging.info('Нет сессий для работы')
		exit()

	client.scheduler.start()
	await client.tasks_watcher()
	#await asyncio.Event().wait()

if __name__ == '__main__':
	proxy_client = ProxyManager(proxies)
	asyncio.run(main())