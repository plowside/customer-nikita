# -*- coding: UTF-8 -*-
import telethon, logging, asyncio, random, httpx, socks, uuid, time, os

from telethon import TelegramClient, functions, events, types
from telethon.tl.functions.messages import GetHistoryRequest, ImportChatInviteRequest, CheckChatInviteRequest, GetPeerDialogsRequest
from telethon.tl.functions.channels import JoinChannelRequest, LeaveChannelRequest
from telethon.tl.functions.contacts import AddContactRequest
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.types import InputPhoneContact
from telethon.errors import rpcerrorlist
from tg_bot import main as tg_bot_func

from config import *

##############################################################################
logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s', level=logging.INFO)
logging.getLogger('aiogram').setLevel(logging.WARNING)
logging.getLogger('telethon').setLevel(logging.WARNING)
logging.getLogger('httpx').setLevel(logging.WARNING)


##############################################################################
proxies = [x.strip() for x in open(proxies, 'r', encoding='utf-8').read().splitlines()]
sessions = [f'{sessions}/{x}' for x in os.listdir(sessions) if x.split('.')[-1] == 'session']



async def send_msg(sender: int, text: str, parse_mode = 'HTML'):
	async with httpx.AsyncClient() as aclient:
		try: await aclient.post(f'https://api.telegram.org/bot{bot_token}/sendMessage', json={'chat_id': sender, 'text': text, 'parse_mode': parse_mode, 'reply_markup': {'inline_keyboard': [ [{ 'text': '❌ Закрыть', 'callback_data': 'utils:close' }] ]}})
		except: ...

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
	def __init__(self, clients_ttl):
		self.clients = {'offline': {}, 'online': {}}
		self.tasks = {}
		self.clients_ttl = clients_ttl
		self.start_times = {}

	async def init_session(self, session):
		client = TelegramClient(session, 69696969, 'qwertyuiopasdfghjklzxcvbnm1234567', flood_sleep_threshold=120, system_lang_code='en', system_version='4.16.30-vxCUSTOM')
		self.clients['offline'][session] = client

	async def check_sessions_timeout(self):
		while True:
			await asyncio.sleep(10)
			if len(self.tasks) > 0:
				continue
			now = asyncio.get_event_loop().time()
			to_remove = []
			for session_key, start_time in list(self.start_times.items()):
				if now - start_time >= self.clients_ttl:
					client = self.clients['online'].pop(session_key)
					await client.disconnect()
					self.clients['offline'][session_key] = client
					to_remove.append(session_key)
			for key in to_remove:
				del self.start_times[key]

	async def run_client(self, client):
		try: await client.connect()
		except ConnectionError:	
			await client.disconnect()
			logging.info(f'[{session}] Ошибка подключения к сессии')
			return
		except rpcerrorlist.FloodWaitError: 
			await client.disconnect()
			logging.info(f'[{session}] Лимит авторизаций')
			return
		except:
			await client.disconnect()
			logging.info(f'[{session}] Неизвестная ошибка аккаунта')
			return
		
		if not await client.is_user_authorized():
			await client.disconnect()
			logging.info(f'[{session}] Мертвая сессия')
			return
		await client.start()
		session_filename = client.session.filename
		self.clients['online'][session_filename] = client
		self.start_times[session_filename] = asyncio.get_event_loop().time()

	async def run_clients(self, amount: int = 99999):
		clients = list(self.clients['offline'].keys())[0:amount]
		tasks = []
		for client_key in clients:
			client = self.clients['offline'].pop(client_key, None)
			if not client: continue
			proxy = proxy_client.get_proxy()
			client.proxy = (socks.HTTP if proxy_protocol['http'] else socks.SOCKS5, proxy[0], int(proxy[1]), True, proxy[2], proxy[3]) if proxy else None
			task = self.run_client(client)
			tasks.append(task)
		await asyncio.gather(*tasks)
		return clients

	async def send_report(self, client, username, peer, reason: str = types.InputReportReasonSpam, message: str = ''):
		try:
			user = await client.get_entity(username)
			peer = peer(user.id, user.access_hash)
			await client(functions.account.ReportPeerRequest(peer=peer, reason=reason, message=message if message else ''))
			return (True, None)
		except Exception as e:
			print(e)
			return (False, e)
		return (False, None)

	async def start_report(self, sender_id, amount: int, username: str, peer, reason, message: str):
		task_uuid = str(uuid.uuid4())
		self.tasks[task_uuid] = True
		online_amount = len(self.clients['online'])
		need_amount = amount - online_amount
		if need_amount > 0: await self.run_clients(need_amount)
		clients = [self.clients['online'][x] for x in list(self.clients['online'].keys())[0:amount]]
		tasks = []
		# await send_msg(6315225351, f'sender_id={sender_id}\namount={amount}\npeer={peer}\nreason={reason}\n{len(self.clients["offline"])}|{len(self.clients["online"])}')
		v = 0
		for client in clients:
			result = await self.send_report(client, username, peer, reason, message if isinstance(message, (str, int, float)) else random.choice(message) if isinstance(message, list) else None)
			#await send_msg(6315225351, f'{result}', parse_mode=None)
			if result[0]:
				v += 1
				await asyncio.sleep(*reports_range)

		del self.tasks[task_uuid]
		await send_msg(sender_id, f'<b>✅ Отправка репорта завершена</b>\n\n<i>Отправлено {v} из {amount} репортов</i>')


	async def get_user_id(self, username):
		for client in self.clients['online'].values():
			try:
				user = await client.get_entity(username)
				return user
			except ValueError as e:
				if "Cannot find any entity corresponding to" in str(e):
					return None
				continue
			except Exception as e:
				logging.error(f"Ошибка при получении user_id через {client.session.filename}: {e}")

		while True:
			if len(self.clients['offline']) == 0:
				logging.info("Нет доступных оффлайн-сессий для запуска.")
				break

			client_keys = await self.run_clients(1)
			if not client_keys:
				break

			client_key = client_keys[0]
			client = self.clients['online'][client_key]
			try:
				user = await client.get_entity(username)
				return user
			except ValueError as e:
				if "Cannot find any entity corresponding to" in str(e):
					return None
				continue
			except Exception as e:
				logging.error(f"Ошибка при получении user_id через {client.session.filename}: {e}")

		logging.info(f"Не удалось найти user_id для username: {username}")
		return None




async def main():
	await proxy_client.proxy_check()

	client = sessions_manager(clients_ttl=clients_ttl)
	future = asyncio.create_task(client.check_sessions_timeout())
	future = asyncio.create_task(tg_bot_func(client))
	tasks = []
	for session in sessions:
		tasks.append(client.init_session(session))
	asyncio.gather(*tasks)

	if len(client.clients) == 0:
		logging.info('Нет сессий для работы')
	logging.info('Скрипт запущен')
	await future

if __name__ == '__main__':
	proxy_client = ProxyManager(proxies)
	asyncio.run(main())