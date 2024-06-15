import subprocess, threading, requests, asyncio, zipfile, shutil, json, os, re

from telethon.sync import TelegramClient
from telethon import types
from telethon import events


os.makedirs('sessions', exist_ok=True)
if os.path.exists('temp'): shutil.rmtree('temp')
os.makedirs('temp', exist_ok=True)
os.makedirs('archives', exist_ok=True)





def create_app(phone, stel_token = None):
	ses = requests.Session()
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
		print('Не удалось создать приложение из-за большого количества попыток')
		return False, (None, None)
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
	#print(f'Получен hash: {hash}')
	resp = ses.post('https://my.telegram.org/apps/create', headers=headers, data={'hash': hash,'app_title': 'plowside','app_shortname': 'everything','app_url': 'my.telegram.org','app_platform': 'desktop','app_desc': ''})

	# Получаем api_id, api_hash
	resp = ses.get('https://my.telegram.org/apps', headers=headers)
	result = re.findall(r'this\.select\(\);">(.*)<', resp.text)
	if len(result) == 2:
		api_id, api_hash = result
		api_id = api_id.split('>')[1].split('<')[0]
		print(f'Получены данные: api_id = {api_id} | api_hash = {api_hash}')
		return True, (api_id, api_hash)


def run_telegram():
	global telegram_process
	telegram_process = subprocess.Popen(['Telegram_desktop/Telegram.exe'])


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
	try:
		shutil.rmtree('Telegram_desktop/tdata')
	except:pass
	os.rename(f'temp/{tdata}/tdata', 'Telegram_desktop/tdata')
	thread = threading.Thread(target=run_telegram)
	thread.start()
	tdata_info = json.load(open(f'temp/{tdata}/{tdata_info_file[0]}', 'r', encoding='utf-8'))
	if tdata_info['phone'] == '261322461842':
		stel_token = 'eef7dcbc9d552dfe889aac7f3a53fa65eef7dcb0eef79d82389a4340029bc785515bf'
	elif tdata_info['phone'] == '261322552192':
		stel_token = 'd977ae75923e1b22bf1adf260dd388acd977ae79d977eefa3fb6daf1df8b7fb90dc61'
	else:
		stel_token = None
	status, (api_id, api_hash) = create_app(tdata_info['phone'], stel_token)
	if not status:
		continue
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
	telegram_process.terminate()
	telegram_process.wait()
	print(f'Сессия успешно создана\nФайл: {me.id}.session\n\n')
	os.remove(f'archives/{tdata}')