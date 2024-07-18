# -*- coding: UTF-8 -*-
import traceback, datetime, telethon, logging, asyncio, random, httpx, socks, json, time, re, os

from telethon import TelegramClient, functions, events, types
from telethon.tl.functions.messages import GetHistoryRequest, ImportChatInviteRequest, CheckChatInviteRequest, GetPeerDialogsRequest
from telethon.tl.functions.channels import JoinChannelRequest, LeaveChannelRequest
from telethon.tl.functions.contacts import AddContactRequest
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.types import InputPhoneContact
from telethon.errors import rpcerrorlist
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import *

##############################################################################
logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s', level=logging.INFO)
logging.getLogger('apscheduler').setLevel(logging.WARNING)
logging.getLogger('telethon').setLevel(logging.WARNING)
logging.getLogger('aiogram').setLevel(logging.WARNING)
logging.getLogger('httpx').setLevel(logging.WARNING)

version = 1.0
##############################################################################
proxies = [x.strip() for x in open(proxies, 'r', encoding='utf-8').read().splitlines()]
sessions = [f'{sessions}/{x}' for x in os.listdir(sessions) if x.split('.')[-1] == 'session']







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
			if version != resp['autoprofile']:
				logging.warning(f'\n\n\nДоступна новая версия скрипта: {resp["autoprofile"]} | Скачать: https://github.com/plowside/customer-nikita\n\n\n')
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
	def __init__(self):
		self.clients = {}
		self.clients_id = {}
		self.scheduler = AsyncIOScheduler()
		self.lock = asyncio.Lock()

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
		logging.info(f'[{session}] Успешно подключился к сессии: [{self.clients[client].id}|{self.clients[client].username}]')

		self.scheduler.add_job(self.avatar_update, trigger='date', run_date=self.scheduler_calculate_run_time(schedulers['avatar_update']), args=(self.clients[client].id, ))


	def scheduler_calculate_run_time(self, schedule: dict):
		return datetime.datetime.now() + datetime.timedelta(days=random.randint(*schedule.get('days', (0, 0))), hours=random.randint(*schedule.get('hours', (0, 0))), minutes=random.randint(*schedule.get('minutes', (0, 0))), seconds=random.randint(*schedule.get('seconds', (0, 0))))

	async def avatar_update(self, client_id):
		self.scheduler.add_job(self.avatar_update, trigger='date', run_date=self.scheduler_calculate_run_time(schedulers['avatar_update']), args=(client_id, ))
		client = self.clients_id[client_id]
		avatars = os.listdir(avatars_path)
		if len(avatars) == 0:
			logging.warning(f'[{client_id}] Нет доступных изображений для установки аватарки')
			return
		avatar = random.choice(avatars)
		logging.info(f'[{client_id}] Устанавливаю аватарку {avatar}')

		try:
			await client(functions.photos.UploadProfilePhotoRequest(file=await client.upload_file(f'{avatars_path}/{avatar}')))
			logging.info(f'[{client_id}] Успешно установил аватарку')
		except Exception as e: logging.error(f'[{client_id}] Не удалось установить аватарку: {e}')

		if remove_avatar_after_use:
			try: os.remove(f'{avatars_path}/{avatar}')
			except Exception as e: logging.error(f'[{client_id}|{avatar}] Не удалось удалить файл аватарки: {e}')




async def main():
	await check_version()
	await proxy_client.proxy_check()
	client = sessions_manager()

	for session in sessions:
		await client.init_session(session)

	if len(client.clients) == 0:
		logging.info('Нет сессий для работы')
		exit()

	client.scheduler.start()
	print('\n\n')
	logging.info('Шедулеры запущены. Скрипт запущен.')
	await asyncio.Event().wait()

if __name__ == '__main__':
	proxy_client = ProxyManager(proxies)
	asyncio.run(main())