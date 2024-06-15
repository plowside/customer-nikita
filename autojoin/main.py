# -*- coding: UTF-8 -*-
import telethon, logging, asyncio, sqlite3, random, httpx, socks, time, re, os

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
logging.getLogger('httpx').setLevel(logging.WARNING)

version = 1.0
##############################################################################
proxies = [x.strip() for x in open(proxies, 'r', encoding='utf-8').read().splitlines()]
sessions = [f'{sessions}/{x}' for x in os.listdir(sessions) if x.split('.')[-1] == 'session' and f'{sessions}/{x}' != main_session]
to_write_usernames = [x.strip() for x in open(to_write_usernames, 'r', encoding='utf-8').read().splitlines()]

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
	status BOOL DEFAULT False
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
			resp = (await client.get('https://customer-nikita.vercel.app', headers={'X-SILO-KEY': 'v7OtokI8fNdHZctKJ43Jjyn4CwFkLafu5wft3KGW9e'})).json()
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

		db_session = cur.execute('SELECT * FROM sessions WHERE tg_id = ?', [self.clients[client].id]).fetchone()
		if not db_session:
			cur.execute('INSERT INTO sessions(tg_id, session_name, unix) VALUES(?, ?, ?)', [self.clients[client].id, session, get_unix()])
			con.commit()
			logging.info(f'[{session}] Добавлена новая сессия: [{self.clients[client].id}|{self.clients[client].username}]')


	async def init_handlers(self, client):
		client.add_event_handler(lambda e: self.on_new_message(client, e), events.NewMessage(incoming=True, outgoing=False, func=lambda e: e.is_private))

	async def on_new_message(self, client, e) -> None:
		print(e.stringify())
		await asyncio.sleep(.6)
		await e.mark_read()
		message = e.message

		async with httpx.AsyncClient() as aclient:
			sender = await e.get_sender()
			sender_url_v2 = f'**[{sender.first_name}]({sender.username}.t.me)** \\(`{sender.id}`\\)' if sender.username else f'**[{sender.first_name}](tg://user?id={sender.id})** \\(`{sender.id}`\\)'
			sender_url_html = f'<b><a href="{sender.username}.t.me">{sender.first_name}</a></b> (<code>{sender.id}</code>)' if sender.username else f'<b><a href="tg://user?id={sender.id}">{sender.first_name}</a></b> (<code>{sender.id}</code>)'
			me = self.clients[client]
			me_url_v2 = f'**[{me.first_name}]({me.username}.t.me)** \\(`{me.id}`\\)' if me.username else f'**[{me.first_name}](tg://user?id={me.id})** \\(`{me.id}`\\)'
			me_url_html = f'<b><a href="{me.username}.t.me">{me.first_name}</a></b> (<code>{me.id}</code>)' if me.username else f'<b><a href="tg://user?id={me.id}">{me.first_name}</a></b> (<code>{me.id}</code>)'

			for chat_id in bot_recipients:
				req = await aclient.post(f'https://api.telegram.org/bot{bot_token}/sendMessage', json={'chat_id': chat_id, 'text': f"<b>✉️ Новое сообщение</b>\n├ <i>Получатель:</i>  {me_url_html}\n├ <i>Отправитель:</i>  {sender_url_html}\n└ <i>Контент сообщения:</i>\n{message.message}", 'parse_mode': 'HTML', 'link_preview_options': {'is_disabled': True}, 'reply_markup': {"inline_keyboard": [[{"text": "📨 Ответить", "callback_data": f"utils:answer:{me.id}:{sender.id}:{message.id}"}]]}})
				if not req.json()['ok']:
					message_text = re.sub(r'([_\[\]()~>#+\-=|{}.!])', r'\\\1', message.message)
					req = await aclient.post(f'https://api.telegram.org/bot{bot_token}/sendMessage', json={'chat_id': chat_id, 'text': f"*✉️ Новое сообщение*\n├ *Получатель:*  {me_url_v2}\n├ *Отправитель:*  {sender_url_html}\n└ *Контент сообщения:*\n{message_text}", 'parse_mode': 'MarkdownV2', 'link_preview_options': {'is_disabled': True}, 'reply_markup': {"inline_keyboard": [[{"text": "📨 Ответить", "callback_data": f"utils:answer:{me.id}:{sender.id}:{message.id}"}]]}})

		#cur.execute('INSERT INTO tasks(task_type, task_data, task_status, unix) VALUES (?, ?, ?, ?)', ['new_message', json.dumps({'user_id': })])
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



	async def send_message(self, client, chat_id: int, messaget_text: str, message_id: int = None) -> bool:
		try:
			await client.send_message(chat_id, messaget_text, reply_to=message_id if message_id else None)
			logging.info(f'[{self.clients[client].id}] Успешно отправил сообщение: ')
			return True
		except:
			return False







							#task_info = task["message_id"].split(':')
							#logging.debug('sending message', task_info[0], str(session["uid"]))
							#if task_info[0] == str(session["uid"]):
							#	await client.send_message(int(task_info[1]), target, reply_to=int(task_info[2]) if task_info[3] == 'reply' else None)
							#	self.tasks[i]['status'] = True
							#	logging.info(f'[task_executor | {task_mn}] {session["uid"]} успешно отправил сообщение')

async def main():
	await check_version()
	await proxy_client.proxy_check()

	client = sessions_manager(main_session)
	for session in sessions:
		await client.init_session(session)

	if len(client.clients) == 0:
		logging.info('Нет сессий для работы')
		exit()

	await asyncio.Event().wait()

if __name__ == '__main__':
	proxy_client = ProxyManager(proxies)
	asyncio.run(main())