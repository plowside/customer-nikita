#!/usr/bin/python
# -*- coding: UTF-8 -*-
import socks, asyncio, traceback, telethon, logging, random, httpx, json, time, sys, os
from datetime import timezone
from telethon import TelegramClient, events
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.photos import UploadProfilePhotoRequest
from telethon.tl.types import *
from telethon.tl import functions
from telethon.errors import rpcerrorlist

from config import *
##############################################################################
logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s', level=logging.INFO)
logging.getLogger('telethon').setLevel(logging.WARNING)

##############################################################################
accounts = [(f"{path_sessions}/{x.replace('.session','')}", x.replace('.session','')) for x in os.listdir(path_sessions) if 'journal' not in x.split('.')[1]]
avatars = [f"{path_avatars}/{x}" for x in os.listdir(path_avatars)]
names = [x for x in open(path_names, 'r', encoding='utf-8').readlines()]
surnames = [x for x in open(path_surnames, 'r', encoding='utf-8').readlines()]
bios = [x for x in open(path_bio, 'r', encoding='utf-8').readlines()]
logging.info(f'Запуск скрипта\n\nКоличество сессий: {len(accounts)}\nСтроки для заполнения:\n\tАватарки [{to_change["avatar"]}]: {len(avatars)}\n\tФамилии [{to_change["name_surname"]}]: {len(surnames)}\n\tИмена [{to_change["name_surname"]}]: {len(names)}\n\tБио [{to_change["bio"]}]: {len(bios)}\n\n\n\n')


async def proxy_check(proxies):
	async with httpx.AsyncClient(proxies=proxies) as client:
		try:
			if (await client.get('http://ip.bablosoft.com')).status_code == 407: raise httpx.ProxyError('Хуйня прокси')
		except Exception as error:
			logging.critical('Невалидные прокси, завершаю скрипт...')
			sys.exit(0)
_proxy = proxy.split(':') if proxy else None

##############################################################################
class client_parser:
	def __init__(self, client, mode, **kwargs):
		self.client = client
		self.mode = mode
		match self.mode:
			case 'channels' | 'dm':
				self._spam_channels = kwargs['spam_channels']
				self.spam_channels = {}

			case 'stories':
				self._parse_chats = kwargs.get('parse_chats') if kwargs.get('parse_chats') else []
				self.parse_chats = []

			case 'invite_to':
				self._parse_chats = kwargs.get('parse_chats') if kwargs.get('parse_chats') else []
				self.parse_chats = []
				self._parse_invites = kwargs.get('parse_invites') if kwargs.get('parse_invites') else []
				self.parse_invites = []


	async def sync_channels(self):
		match self.mode:
			case 'channels' | 'dm':
				async for dialog in self.client.iter_dialogs(): #InputPeerChannel, InputPeerSelf, InputPeerUser, InputPeerChat
					if True not in [isinstance(dialog.input_entity, x) for x in check_mode]: continue # Проверка по check_mode

					if len(self._spam_channels) > 0:
						if True not in [x in (dialog.name, dialog.entity.id) for x in self._spam_channels]: continue # Проверка на цель "где искать посты"

						target = dialog.entity.id
						text = default_message
						try: text = self._spam_channels[target] if self._spam_channels[target] else default_message
						except: pass

						self.spam_channels[target] = text
					else:
						target = dialog.entity.id
						text = default_message

						self.spam_channels[target] = text


				logging.info(f'Количество целей: {len(self.spam_channels)}')
				logging.debug(f'Полученые id целей:\n{json.dumps(self.spam_channels, indent=4)}')
			
			case 'stories':
				async for dialog in self.client.iter_dialogs(): #InputPeerChannel, InputPeerSelf, InputPeerUser, InputPeerChat
					if True not in [isinstance(dialog.input_entity, x) for x in check_mode]: continue # Проверка по check_mode

					if len(self._parse_chats) > 0:
						if True not in [x in (dialog.name, dialog.entity.id) for x in self._parse_chats]: continue # Проверка на цель "откуда приглашать"

					self.parse_chats.append(dialog.entity.id)


				logging.info(f'Количество целей: {len(self.parse_chats)}')
				logging.debug(f'Полученые id целей:\n{json.dumps(self.parse_chats, indent=4)}')

			case 'invite_to':
				async for dialog in self.client.iter_dialogs(): #InputPeerChannel, InputPeerSelf, InputPeerUser, InputPeerChat
					try:
						if dialog.entity.megagroup:
							if True in [x in (dialog.name, dialog.entity.id) for x in self._parse_invites]: self.parse_invites.append(dialog.entity.id)
					except: pass

					if True not in [isinstance(dialog.input_entity, x) for x in check_mode]: continue # Проверка по check_mode
					if len(self._parse_chats) > 0:
						if True not in [x in (dialog.name, dialog.entity.id) for x in self._parse_chats]: continue # Проверка на цель "откуда приглашать"


					self.parse_chats.append(dialog.entity.id)


				logging.info(f'Количество целей [откуда]: {len(self.parse_chats)}')
				logging.info(f'Количество целей [куда]: {len(self.parse_invites)}')
				logging.debug(f'Полученые id целей [откуда]:\n{json.dumps(self.parse_chats, indent=4)}')
				logging.debug(f'Полученые id целей [куда]:\n{json.dumps(self.parse_invites, indent=4)}')


##############################################################################
async def main_channels(session):
	session, session_name = session
	client = TelegramClient(session, 69696969, 'qwertyuiopasdfghjklzxcvbnm1234567', device_model = "iPhone 13 Pro Max", system_version = "14.8.1", app_version = "10.6", lang_code = "en", system_lang_code = "en-US", proxy=(socks.HTTP, _proxy[0], int(_proxy[1]), True, _proxy[2], _proxy[3]) if proxy else None)
	await client.start()

	data = client_parser(client, mode, spam_channels=spam_channels)
	await data.sync_channels()


	@client.on(events.NewMessage(chats=data.spam_channels))
	async def message_handler(event):
		message = event.message
		try:
			channel_id = message.peer_id.channel_id; 
			if (not message.replies.comments) or (not message.post): return
		except AttributeError: return
		except Exception as error: return logging.error(f'[{session_name}] Ошибка при получении объекта [{message.peer_id}]: {error}')
		

		if generate_text and openai_api_key:
			try:
				async with httpx.AsyncClient(proxies=proxies) as aclient:
					req = (await aclient.post('https://api.openai.com/v1/chat/completions', headers={'Content-Type':'application/json','Authorization': f'Bearer {openai_api_key}'}, json={'model':'gpt-3.5','messages': [{"role": "system", "content": "Ты девушка.И пишеш кратко, до 11 слов."}, {"role": "user", "content": f"Придумай осмысленный человекоподобный комментарий, до 11 слов к посту: {message.message}"}], 'temperature': 0.7})).json()
				if 'choices' in req: text = req['choices'][0]['message']['content'].strip()
				else: text = random.choice(gpt_not_working_answer_variants)

				if len(text) == 0: text = random.choice(gpt_not_working_answer_variants)
			except Exception as e:
				logging.error(f'[{session_name} | LINE:{traceback.extract_tb(e.__traceback__)[-1].lineno}] Не удалось сгенерировать комментарий ({type(e)}): {e}\n{traceback.format_exc()}')
				text = random.choice(gpt_not_working_answer_variants)
		else:
			text = data.spam_channels[channel_id] if isinstance(data.spam_channels[channel_id], str) else random.choice(data.spam_channels[channel_id])
		print('text', text)
		try:
			await asyncio.sleep(random.randint(*time_before_message))
			if isinstance(text, dict): await client.send_file(channel_id, Document(id=text['id'], access_hash=text['access_hash'], file_reference=b'\x00f\xab\xbf\xa9:{\x10\xa8\xcc\x9aO\xc9(\xd6\xe2\xfc\xf7\xdd\xa0T', date=datetime(2018, 12, 23, 3, 40, 1, tzinfo=timezone.utc), mime_type='image/webp', size=0, dc_id=5, attributes=[], thumbs=[], video_thumbs=[]), comment_to=message.id)
			else: await client.send_message(entity=channel_id, message=text, comment_to=message.id)
			logging.info(f'[{session_name}] Прокомментировал пост')
		except Exception as error: logging.error(f'[{session_name} | LINE:{traceback.extract_tb(error.__traceback__)[-1].lineno}] Ошибка при отправке комментария: {error}')



	await client.start()
	try: await client.run_until_disconnected()
	except: await client.disconnect()



async def main_dm(session):
	session, session_name = session
	client = TelegramClient(session, 69696969, 'qwertyuiopasdfghjklzxcvbnm1234567', device_model = "iPhone 13 Pro Max", system_version = "14.8.1", app_version = "10.6", lang_code = "en", system_lang_code = "en-US", proxy=(socks.HTTP, _proxy[0], int(_proxy[1]), True, _proxy[2], _proxy[3]) if proxy else None)
	await client.start()

	data = client_parser(client, mode, spam_channels=spam_channels)
	await data.sync_channels()

	count = 0

	logging.info(f'[{session_name}] Начинаю писать людям...\n\n')
	try:
		for entity in [await client.get_entity(x) for x in data.spam_channels]:
			try:
				users = await client.get_participants(entity.id)
			except telethon.errors.rpcerrorlist.ChatAdminRequiredError: continue
			except Exception as error:
				logging.error(f'[{session_name}] Неудалось получить участников [{entity.id}]: {error}')
				continue

			for user in users:
				if count > 24:
					count = 0
					await asyncio.sleep(300)

				user_entity = await client.get_entity(user.id)
				try:
					text = data.spam_channels[entity.id] if isinstance(data.spam_channels[entity.id], str) else random.choice(data.spam_channels[entity.id])
					await client.send_message(InputPeerUser(user_entity.id, user_entity.access_hash), text)
					logging.info(f'[{session_name}] Написал {user_entity.id}: "{f"{text[:10]}...{text[-5:]}" if len(text) >= 15 else text}"')
					count+=1
				except: pass
	except Exception as error: logging.error(f'[{session_name}] Глобальная ошибка: {error}')


	await client.disconnect()
	logging.info(f'[{session_name}] Работа скрипта завершена\nВсего отправлено сообщений: {count}')
	sys.exit()


async def main_stories(session):
	session, session_name = session
	client = TelegramClient(session, 69696969, 'qwertyuiopasdfghjklzxcvbnm1234567', device_model = "iPhone 13 Pro Max", system_version = "14.8.1", app_version = "10.6", lang_code = "en", system_lang_code = "en-US", proxy=(socks.HTTP, _proxy[0], int(_proxy[1]), True, _proxy[2], _proxy[3]) if proxy else None)
	await client.start()
	
	data = client_parser(client, mode, parse_chats=parse_chats)
	await data.sync_channels()
	valid = 0

	logging.info(f'[{session_name}] Начинаю искать истории...\n\n')
	for target in data.parse_chats:
		try:
			target = await client.get_entity(target)

			users = await client.get_participants(target.id)
			for user in users:
				if not user.username or not user.premium: continue
				try:
					result = await client(functions.stories.ReadStoriesRequest(
						peer=user.username,
						max_id=99999999
					))
					if len(result) > 0:
						for x in result:
							try: await client(functions.stories.SendReactionRequest(peer=user.username, story_id=x, reaction=ReactionEmoji(emoticon='❤'), add_to_recent=True))
							except: pass
						valid += len(result)
						logging.info(f'[{session_name}] Просмотрел истории [@{user.username}]: {len(result)} шт.{" | Поставил лайки историям" if True else ""}')
				except (telethon.errors.rpcbaseerrors.BadRequestError): pass
				except Exception as e: logging.error(f'[{session_name}] Ошибка при просмотре историй [@{user.username}]: {e}')
		except (telethon.errors.rpcerrorlist.UsernameInvalidError, telethon.errors.rpcerrorlist.UsernameNotOccupiedError, telethon.errors.rpcbaseerrors.BadRequestError): pass
		except Exception as e: logging.error(f'[{session_name}] Ошибка при получении чата или участников чата [{target.id}]: {e}')
	
	await client.disconnect()
	logging.info(f'[{session_name}] Работа скрипта завершена\nВсего просмотрено историй: {valid}')
	sys.exit()


async def main_invite(session):
	session, session_name = session
	client = TelegramClient(session, 69696969, 'qwertyuiopasdfghjklzxcvbnm1234567', device_model = "iPhone 13 Pro Max", system_version = "14.8.1", app_version = "10.6", lang_code = "en", system_lang_code = "en-US", proxy=(socks.HTTP, _proxy[0], int(_proxy[1]), True, _proxy[2], _proxy[3]) if proxy else None)
	await client.start()
	
	data = client_parser(client, mode, parse_chats=parse_chats, parse_invites=parse_invites)
	await data.sync_channels()

	logging.info(f'[{session_name}] Получаю пригласительные ссылки...\n')
	invite_to = [await client.get_input_entity(_x) for _x in data.parse_invites]
	logging.info(f'[{session_name}] Удалось получить {len(invite_to)} из {len(data.parse_invites)} ссылок')

	if len(invite_to) > 0:
		logging.info(f'[{session_name}] Приглашаю людей...\n\n')
		for target in data.parse_chats:
			try:
				target = await client.get_entity(target)

				users = await client.get_participants(target.id)
				_users = [x.username for x in users if x.username]
				
				for x in invite_to:
					try:
						result = await client(functions.channels.InviteToChannelRequest(channel=x, users=_users))
					except telethon.errors.rpcerrorlist.PeerFloodError: logging.info("[{session_name}] Ошибка от телеграма: флуд")
					except telethon.errors.rpcerrorlist.UserPrivacyRestrictedError: pass
					except Exception as e: logging.error(f'[{session_name}] Ошибка при отправке приглашения: {e}')
			except (telethon.errors.rpcerrorlist.UsernameInvalidError, telethon.errors.rpcerrorlist.UsernameNotOccupiedError, telethon.errors.rpcbaseerrors.BadRequestError): pass
			except Exception as e: logging.error(f'[{session_name}] Ошибка при получении чата или участников чата [{target.id}]: {e}')
	
	await client.disconnect()
	logging.info(f'[{session_name}] Работа скрипта завершена')
	sys.exit()




async def prepare_session(session):
	session, session_name = session
	client = TelegramClient(session, 69696969, 'qwertyuiopasdfghjklzxcvbnm1234567', device_model = "iPhone 13 Pro Max", system_version = "14.8.1", app_version = "10.6", lang_code = "en", system_lang_code = "en-US", proxy=(socks.HTTP, _proxy[0], int(_proxy[1]), True, _proxy[2], _proxy[3]) if proxy else None)

	logging.info(f'[{session_name}] Подключаюсь к сессии.')
	try: await client.connect()
	except ConnectionError:	
		logging.info(f'[{session_name}] Ошибка подключения к сессии, беру другой аккаунт\n\n')
		return (session, False)
	except rpcerrorlist.FloodWaitError: 
		logging.info(f'[{session_name}] Лимит авторизаций, беру другой аккаунт\n\n')
		return (session, False)
	if not await client.is_user_authorized(): 
		logging.info(f'[{session_name}] Мертвая сессия, беру другую\n\n')
		return (session, False)
	else: logging.info(f'[{session_name}] Успешно подключился к сессии\n')

	if to_change['chatlists']:
		for x in open(path_chatlists, 'r', encoding='utf-8').readlines():
			try:
				logging.info(f'[{session_name}] Проверяю чатлист {x}')
				chatlist = await client(functions.chatlists.CheckChatlistInviteRequest(slug=x))
				if isinstance(chatlist, chatlists.ChatlistInviteAlready):
					if len(chatlist.missing_peers) == 0:
						logging.info(f'[{session_name}] Чатлист уже добавлен на аккаунт')
						continue
					await client(functions.chatlists.JoinChatlistInviteRequest(x, chatlist.missing_peers))
					logging.info(f'[{session_name}] Успешно добавил недостающие каналы чатлиста')
				else:
					z = await client(functions.chatlists.JoinChatlistInviteRequest(x, chatlist.peers))
					logging.info(f'[{session_name}] Успешно добавил чатлист')
			except Exception as e:
				if 'INVITE_SLUG_EXPIRED' in str(e):
					logging.info(f'[{session_name}] Неверный/просроченный ID чатлиста')
				else: logging.info(f'[{session_name}] Неудалось проверить чатлист: {e}')
				continue

	if to_change['name_surname'] and (len(names) > 0 or len(surnames) > 0):
		name, surname = random.choice(names) if len(names) else '', random.choice(surnames) if len(surnames) else ''
		logging.info(f'[{session_name}] Устанавливаю имя и фамилию: "{name} {surname}"')
		try: await client(UpdateProfileRequest(first_name=name, last_name=surname))
		except Exception as e: logging.error(f'[{session_name}] Неудалось установить имя и фамилию. Ошибка: {e}')
		logging.info(f'[{session_name}] Имя и Фамилия успешно установлены')
	if to_change['bio'] and len(bios) > 0:
		bio = random.choice(bios)
		logging.info(f'[{session_name}] Устанавливаю био: {bio}')
		try: await client(UpdateProfileRequest(about=bio))
		except Exception as e: logging.error(f'[{session_name}] Неудалось био. Ошибка: {e}')
		logging.info(f'[{session_name}] Био успешно установлено')
	if to_change['avatar'] and len(avatars) > 0:
		avatar = random.choice(avatars)
		logging.info(f'[{session_name}] Устанавливаю аватарку: {avatar}')
		try: await client(UploadProfilePhotoRequest(file=await client.upload_file(avatar)))
		except Exception as e: logging.error(f'[{session_name}] Неудалось установить аватарку. Ошибка: {e}')
		logging.info(f'[{session_name}] Аватарка успешно установлена')
	

	await client.disconnect()
	return (session, True)

##############################################################################


if __name__ == '__main__':
	asyncio.run(proxy_check(proxies))

	match mode:
		case 'invite_to': target = main_invite
		case 'channels': target = main_channels
		case 'stories': target = main_stories
		case 'dm': target = main_dm
		case _: target = None

	if target: 
		async def run_instances(func, data):
			tasks = []
			for x in data:
				task = asyncio.create_task(func(x))
				tasks.append(task)
			return [(x[0], x[0].split('/')[-1]) for x in await asyncio.gather(*tasks) if x and x[1]]
		
		sessions = asyncio.run(run_instances(prepare_session, accounts))
		logging.info('Данные на аккаунтах обновлены, запускаю текущий режим\n\n')
		asyncio.run(run_instances(target, sessions))
	else: logging.info('Вы не выбрали режим работы')