# -*- coding: UTF-8 -*-
import telethon, logging, asyncio, random, httpx, socks, time, os

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

version = 1.1
##############################################################################
text_to_answer = [x.replace('\\n', '\n') for x in open(text_to_answer, 'r', encoding='utf-8').read().splitlines()]
proxies = [x.strip() for x in open(proxies, 'r', encoding='utf-8').read().splitlines()]
sessions = [f'{sessions}/{x}' for x in os.listdir(sessions) if x.split('.')[-1] == 'session']



async def check_version():
	try:
		async with httpx.AsyncClient() as client:
			resp = (await client.get('https://customer-nikita.vercel.app', headers={'X-SILO-KEY': 'v7OtokI8fNdHZctKJ43Jjyn4CwFkLafu5wft3KGW9e'})).json()
			if version != resp['autoanswer']:
				logging.warning(f'\n\n\nДоступна новая версия скрипта: {resp["autoanswer"]} | Скачать: https://github.com/plowside/customer-nikita\n\n\n')
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
	def __init__(self):
		self.clients = {}

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
			return False
		await client.start()

		self.clients[client] = await client.get_me()
		await self.init_handlers(client)
		logging.info(f'[{session}] Успешно подключился к сессии: [{self.clients[client].id}|{self.clients[client].username}]')


	async def init_handlers(self, client):
		client.add_event_handler(lambda e: self.on_new_message(client, e), events.NewMessage(incoming=True, outgoing=False, func=lambda e: e.is_private))

	async def on_new_message(self, client, e):
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


async def main():
	await check_version()
	await proxy_client.proxy_check()

	client = sessions_manager()
	for session in sessions:
		await client.init_session(session)

	if len(client.clients) == 0:
		logging.info('Нет сессий для работы')
		exit()

	await asyncio.Event().wait()

if __name__ == '__main__':
	proxy_client = ProxyManager(proxies)
	asyncio.run(main())