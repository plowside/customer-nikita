# -*- coding: UTF-8 -*-
import traceback, datetime, telethon, logging, asyncio, sqlite3, random, httpx, socks, json, time, re, os

from telethon import TelegramClient, functions, events, types
from telethon.tl.functions.messages import GetHistoryRequest, ImportChatInviteRequest, CheckChatInviteRequest, GetPeerDialogsRequest
from telethon.tl.functions.channels import JoinChannelRequest, LeaveChannelRequest
from telethon.tl.functions.contacts import AddContactRequest
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.types import InputPhoneContact
from telethon.errors import rpcerrorlist

from config import *

##############################################################################
logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s', level=logging.INFO)
logging.getLogger('telethon').setLevel(logging.WARNING)
logging.getLogger('aiogram').setLevel(logging.WARNING)
logging.getLogger('httpx').setLevel(logging.WARNING)

version = 1.1
##############################################################################
text_to_answer = [x.replace('\\n', '\n') for x in open(text_to_answer, 'r', encoding='utf-8').read().splitlines()]
proxies = [x.strip() for x in open(proxies, 'r', encoding='utf-8').read().splitlines()]
sessions = [f'{sessions}/{x}' for x in os.listdir(sessions) if x.split('.')[-1] == 'session' and f'{sessions}/{x}' != main_session]


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
			if version != resp['autoreaction']:
				logging.warning(f'\n\n\nДоступна новая версия скрипта: {resp["autoreaction"]} | Скачать: https://github.com/plowside/customer-nikita\n\n\n')
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
		self.lock = asyncio.Lock()

	async def init_main_session(self):
		await self.main_client.start()
		for channel in channels:
			await self.join_channel(self.main_client, await self.main_client.get_me(), '', channels[channel]['link'])
		
		self.main_client.add_event_handler(lambda e: self.on_new_message(self.main_client, e), events.NewMessage(chats=list(channels.keys())))

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

		async with self.lock:
			db_session = cur.execute('SELECT * FROM sessions WHERE tg_id = ?', [self.clients[client].id]).fetchone()
			if not db_session:
				cur.execute('INSERT INTO sessions(tg_id, session_name, unix) VALUES(?, ?, ?)', [self.clients[client].id, session, get_unix()])
				con.commit()
				logging.info(f'[{session}] Добавлена новая сессия: [{self.clients[client].id}|{self.clients[client].username}]')


	async def init_handlers(self, client):
		client.add_event_handler(lambda e: self.on_new_message_(client, e), events.NewMessage(incoming=True, outgoing=False, func=lambda e: e.is_private))


	# Хендлер нового сообщения через main_session
	async def on_new_message(self, client, e) -> None:
		message = e.message
		channel_id = message.peer_id.channel_id
		if '⠀ ⠀⠀' in message.message:
			logging.info(f'Пропущен рекламный пост: [{channel_id}|{message.id}]')
			return
		if not str(channel_id).startswith('-100'): channel_id = int(f'-100{channel_id}')
		reaction = random.choice(channels[channel_id]['reactions'])
	
		async with self.lock:
			cur.execute('INSERT INTO tasks (task_type, task_data, task_status, unix) VALUES (?, ?, ?, ?)', ['set_reaction', json.dumps({'channel_id': channel_id, 'message_id': message.id, 'link': f"{channels[channel_id]['link']}", 'start_reaction': reaction}), 'created', get_unix()])
			con.commit()
	
		await client(functions.messages.SendReactionRequest(peer=channel_id, msg_id=message.id, big=True, add_to_recent=True, reaction=[types.ReactionCustomEmoji(int(reaction)) if reaction.isnumeric() else types.ReactionEmoji(reaction)]))
		logging.info(f'Новая задача: [{channel_id}|{message.id}]')



	async def on_new_message_(self, client, e):
		await asyncio.sleep(.3)
		await client(functions.account.UpdateStatusRequest(offline=False))
		await asyncio.sleep(.6)
		await e.mark_read()
		await asyncio.sleep(random.randint(*time_to_answer))

		await e.respond(random.choice(text_to_answer))
		sender = await e.get_sender()
		if not sender.contact:
			await asyncio.sleep(1.3)
			await client(AddContactRequest(id=sender.id, phone='i need that phone', first_name=sender.first_name if sender.first_name else '', last_name=sender.last_name if sender.last_name else '', add_phone_privacy_exception=False))
			logging.info(f'Ответил и Добавил пользователя ({sender.id}) в контакты')
		else:
			logging.info(f'Ответил пользователю ({sender.id})')
		await asyncio.sleep(3)
		await client(functions.account.UpdateStatusRequest(offline=True))





	# Выполнитель задач
	async def tasks_watcher(self):
		async with self.lock:
			tasks = cur.execute('SELECT * FROM tasks WHERE task_status = ?', ['in_progress']).fetchall()
		for task in tasks:
			match task['task_type']:
				case 'set_reaction':
					task['task_data'] = json.loads(task['task_data'])
					await self.async_create_task(self.task_executor(task))
		await asyncio.sleep(10)

		while True:
			async with self.lock:
				tasks = cur.execute('SELECT * FROM tasks WHERE task_status = ?', ['created']).fetchall()
			for task in tasks:
				match task['task_type']:
					case 'set_reaction':
						task['task_data'] = json.loads(task['task_data'])
						await self.async_create_task(self.task_executor(task))

			await asyncio.sleep(5)



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
		task_id_text = f"{task_data['channel_id']}|{task_data['message_id']}"
		task_completed = True
		channel_id = task_data['channel_id']
		channel_data = channels[channel_id]
		sessions_count = random.randint(*channel_data['sessions'])
		clients = list(self.clients.items())[:sessions_count]

		time_to_sleep_i = [] 
		temp = sessions_count
		temp3 = 0
		for i_, x in enumerate(channel_data['strategy']):
			if temp <= 0: break
			temp2 = x[1]
			temp3 += x[1]
			if temp2 > temp: temp2 = temp
			time_to_sleep_i.append([temp3, x[0] / temp2])
			temp -= x[1]
		reactions = {x: (80 if x == task_data['start_reaction'] else 30) for x in channel_data['reactions']}
		for i, (client, client_data) in enumerate(clients, start=1):
			if random.random() < chances['skip_session']:
				continue

			time_to_sleep = 10
			for x in time_to_sleep_i:
				if i <= x[0]:
					time_to_sleep = x[1]
					break
			try:
				reaction = random.choices(list(reactions.keys()), list(reactions.values()))[0]
				await client(functions.messages.SendReactionRequest(peer=task_data['link'], msg_id=task_data['message_id'], big=True, add_to_recent=False, reaction=[types.ReactionCustomEmoji(int(reaction)) if reaction.isnumeric() else types.ReactionEmoji(reaction)]))
				logging.info(f'[{task_id_text}|{client_data.id}] Установил реакцию {reaction}')
			except rpcerrorlist.FloodWaitError:
				logging.info(f'[{task_id_text}|{client_data.id}] Антифлуд')
			except rpcerrorlist.ChannelPrivateError:
				logging.error(f'[{task_id_text}|{client_data.id}] Канал приватный либо пользователь заблокирован в нём')
			except Exception as e:
				logging.error(f'[{task_id_text}|{client_data.id} | LINE:{traceback.extract_tb(e.__traceback__)[-1].lineno}] Общая ошибка ({type(e)}): {e}\n{traceback.format_exc()}')
			
			if len(clients) != i:
				await asyncio.sleep(time_to_sleep)


		async with self.lock:
			cur.execute('UPDATE tasks SET task_status = ? WHERE id = ?', ['completed' if task_completed else 'created', task['id']])
			con.commit()
		logging.info(f'[{task_id_text}|{client_data.id}] Задача завершена')

	async def async_create_task(self, task):
		asyncio.get_event_loop().create_task(task)







async def main():
	await check_version()
	await proxy_client.proxy_check()

	client = sessions_manager(main_session)
	await client.init_main_session()
	
	for session in sessions:
		await client.init_session(session)

	if len(client.clients) == 0:
		logging.info('Нет сессий для работы')
		exit()

	await client.tasks_watcher()
	await asyncio.Event().wait()

if __name__ == '__main__':
	proxy_client = ProxyManager(proxies)
	asyncio.run(main())