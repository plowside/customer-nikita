import httpx, time, subprocess, threading, requests, asyncio, zipfile, shutil, json, os, re

from telethon.sync import TelegramClient
from telethon import types
from telethon import events

from config import *


proxies = open(proxies, 'r', encoding='utf-8').read().splitlines()

os.makedirs('sessions', exist_ok=True)
if os.path.exists('temp'): shutil.rmtree('temp')
os.makedirs('temp', exist_ok=True)
os.makedirs('archives', exist_ok=True)


if not os.path.exists('Telegram_desktop/Telegram.exe'):
	print('Скачиваю клиент телеграма')
	resp = requests.get('https://telegram.org/dl/desktop/win64_portable')
	with open('temp/telegram_client.zip', 'wb') as file:
		file.write(resp.content)
	with zipfile.ZipFile('temp/telegram_client.zip', 'r') as zip_ref:
		zip_ref.extractall('temp/telegram_client')
	os.rename('temp/telegram_client/Telegram', 'Telegram_desktop')
	os.remove('temp/telegram_client.zip')
	shutil.rmtree('temp/telegram_client')
	print('Клиент телеграма успешно скачан')






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

proxy_client = ProxyManager(proxies)








def create_app(phone, stel_token = None):
	proxy = proxy_client.get_proxy()
	ses = requests.Session()
	if proxy:
		ses.proxies = {'http': f'http://{proxy[2]}:{proxy[3]}@{proxy[0]}:{proxy[1]}', 'https': f'http://{proxy[2]}:{proxy[3]}@{proxy[0]}:{proxy[1]}'}

	if stel_token:
		jar = requests.cookies.RequestsCookieJar()
		jar.set('stel_token', stel_token, domain='my.telegram.org', path='/')
		ses.cookies.update(jar)
	
	headers = {'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7','accept-language': 'ru','cache-control': 'max-age=0','priority': 'u=0, i','sec-ch-ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"','sec-ch-ua-mobile': '?0','sec-ch-ua-platform': '"Windows"','sec-fetch-dest': 'document','sec-fetch-mode': 'navigate','sec-fetch-site': 'none','sec-fetch-user': '?1','upgrade-insecure-requests': '1','user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'}
	resp = ses.get('https://my.telegram.org/apps', headers=headers)
	result = re.findall(r'this\.select\(\);">(.*)<', resp.text)
	if len(result) == 2:
		api_id, api_hash = result
		api_id = api_id.split('>')[1].split('<')[0]
		print(f'Получены данные: api_id = {api_id} | api_hash = {api_hash}')
		return True, (api_id, api_hash)

	resp = ses.post('https://my.telegram.org/auth/send_password', headers=headers, data={'phone': phone})
	if resp.text == 'Sorry, too many tries. Please try again later.':
		print('Не удалось создать приложение из-за большого количества попыток входа')
		return False, (123, '123')
	random_hash = resp.json()['random_hash']
	#print(f'Получил random_hash: {random_hash}')

	while True:
		password = input(f'Введите отправленный код: ').strip()
		try:
			resp = ses.post('https://my.telegram.org/auth/login', headers=headers, data={'phone': phone,'random_hash': random_hash,'password': password})
			#print(resp.headers)
			if resp.text.lower() != 'true':
				raise 'Invalid_code'
			break
		except:
			print(f'Неверный код')


	# Проверяем наличие созданного приложение
	resp = ses.get('https://my.telegram.org/apps', headers=headers)
	result = re.findall(r'this\.select\(\);">(.*)<', resp.text)
	if len(result) == 2:
		api_id, api_hash = result
		api_id = api_id.split('>')[1].split('<')[0]
		print(f'Получены данные: api_id = {api_id} | api_hash = {api_hash}')
		return True, (api_id, api_hash)

	
	# Создаем приложение
	hash = resp.text.split('name="hash" value="')[1].split('"')[0]
	print(f'Получен hash: {hash}')
	
	retry = 0
	while retry < 3:
		time.sleep(3)
		print(f'Создаю приложение, попытка: {retry+1}')
		resp = ses.post('https://my.telegram.org/apps/create', headers=headers, data={'hash': hash,'app_title': 'plowside','app_shortname': 'everything','app_url': 'my.telegram.org','app_platform': 'desktop','app_desc': ''})

		# Получаем api_id, api_hash
		resp = ses.get('https://my.telegram.org/apps', headers=headers)
		result = re.findall(r'this\.select\(\);">(.*)<', resp.text)
		if len(result) == 2:
			api_id, api_hash = result
			api_id = api_id.split('>')[1].split('<')[0]
			print(f'Получены данные: api_id = {api_id} | api_hash = {api_hash}')
			return True, (api_id, api_hash)

	filename = f'resp_{time.time()}.txt'
	open(filename, 'w', encoding='utf-8').write(resp.text)
	print(f'Не удалось получить api_id и api_hash, ответ от сервера записан в {filename}')
	return False, (123, '123')

def run_telegram():
	global telegram_process
	telegram_process = subprocess.Popen(['Telegram_desktop/Telegram.exe'])

if sessions_type['archives']:
	archives = os.listdir('archives')
	for archive in archives:
		archive_path = f'archives/{archive}'
		with zipfile.ZipFile(archive_path, 'r') as zip_ref:
			extracted_archive_path = f'temp/{archive}'
			zip_ref.extractall(extracted_archive_path)


	tdatas = os.listdir('temp')
	for tdata in tdatas:
		tdata_files = os.listdir(f'temp/{tdata}')
		tdata_info_file = [x for x in tdata_files if '.json' in x]
		if len(tdata_info_file) == 0:
			print(f'[{tdata}] Не удалось найти файл с информацией о тдате')
			continue
		print(f'[{tdata}] Обрабатываю тдату')
		if os.path.exists('Telegram_desktop/tdata'):
			try: shutil.rmtree('Telegram_desktop/tdata')
			except Exception as e: print(f'Не удалось удалить текущую тдату в клиенте телеграма: {e}')
		os.rename(f'temp/{tdata}/tdata', 'Telegram_desktop/tdata')
		thread = threading.Thread(target=run_telegram)
		thread.start()
		tdata_info = json.loads(open(f'temp/{tdata}/{tdata_info_file[0]}', encoding='utf-8').read())
		status, (api_id, api_hash) = create_app(tdata_info['phone'])
		if status:
			client = TelegramClient('temp/temp_session', api_id, api_hash, system_lang_code='en', system_version='4.16.30-vxCUSTOM')
			client.start(phone=tdata_info['phone'], password=open(f'temp/{tdata}/2fa.txt', 'r', encoding='utf-8').read().splitlines()[0] if '2fa.txt' in tdata_files else None)
			me = client.get_me()
			client.session.save()
			client.disconnect()
			try:
				os.rename('temp/temp_session.session', f'sessions/{me.id}.session')
			except:
				os.remove(f'sessions/{me.id}.session')
				os.rename('temp/temp_session.session', f'sessions/{me.id}.session')
			print(f'Сессия успешно создана\nФайл: {me.id}.session')
			os.remove(f'archives/{tdata}')
		try:
			telegram_process.terminate()
			telegram_process.wait()
		except Exception as e: print(e)
		time.sleep(.5)
		print('\n')

if sessions_type['api_id_and_api_hash']:
	for phone, api_id, api_hash in [x.split(',') for x in open('api_id_and_api_hash.txt', 'r', encoding='utf-8').read().splitlines()]:
		client = TelegramClient('temp/temp_session', api_id, api_hash, system_lang_code='en', system_version='4.16.30-vxCUSTOM')
		client.start(phone=phone)
		me = client.get_me()
		client.session.save()
		client.disconnect()
		try:
			os.rename('temp/temp_session.session', f'sessions/{me.id}.session')
		except:
			os.remove(f'sessions/{me.id}.session')
			os.rename('temp/temp_session.session', f'sessions/{me.id}.session')
		print(f'Сессия успешно создана\nФайл: {me.id}.session')
		time.sleep(.5)
		print('\n')