#!/usr/bin/python
# -*- coding: UTF-8 -*-
import socks, asyncio, aiofiles, aiofiles.os, traceback, telethon, logging, random, httpx, json, time, sys, os
from datetime import timezone
from telethon import TelegramClient, events
from telethon.tl.functions.channels import CreateChannelRequest, JoinChannelRequest, UpdateUsernameRequest, EditPhotoRequest
from telethon.tl.functions.messages import GetHistoryRequest, ImportChatInviteRequest, ForwardMessagesRequest, GetDialogFiltersRequest
from telethon.tl.functions.account import UpdatePersonalChannelRequest, UpdateProfileRequest, UpdateNotifySettingsRequest
from telethon.tl.functions.photos import UploadProfilePhotoRequest, DeletePhotosRequest, GetUserPhotosRequest
from telethon.tl.functions.chatlists import LeaveChatlistRequest
from telethon.tl.types import *
from telethon.tl import functions
from telethon.errors import rpcerrorlist, common

from tg_bot import main as tg_bot_func

from config import *

##############################################################################
logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s', level=logging.INFO)
logging.getLogger('telethon').setLevel(logging.WARNING)
logging.getLogger('aiogram').setLevel(logging.WARNING)
logging.getLogger('httpx').setLevel(logging.WARNING)

##############################################################################
def update_b():
	data_dict_b['accounts'] = [(f"{data_dict['path_sessions']}/{x}", x.replace('.session','')) for x in os.listdir(data_dict['path_sessions']) if 'journal' not in x.split('.')[1]]
	data_dict_b['avatars'] = [f"{data_dict['path_avatars']}/{x}" for x in os.listdir(data_dict['path_avatars'])]
	data_dict_b['self_channel_avatars'] = [f"{data_dict['path_channels_avatars']}/{x}" for x in os.listdir(data_dict['path_channels_avatars'])] if data_dict['self_channel']['avatar'] else []
	data_dict_b['names'] = [x for x in open(data_dict['path_names'], 'r', encoding='utf-8').read().splitlines()]
	data_dict_b['surnames'] = [x for x in open(data_dict['path_surnames'], 'r', encoding='utf-8').read().splitlines()]
	data_dict_b['bios'] = [x for x in open(data_dict['path_bio'], 'r', encoding='utf-8').read().splitlines()]
	if data_dict['to_change']['auto_join_ft']: data_dict_b['auto_join_channels'] = [x for x in open(data_dict['path_auto_join'], 'r', encoding='utf-8').read().splitlines()]
	
	proxy = data_dict['proxy']
	_proxy = (proxy.split(':') if '@' not in proxy else f'http://{proxy}') if proxy else None
	data_dict_b['_proxy'] = proxy.split(':') if proxy else None
	data_dict_b['proxies'] = {'http://': _proxy if '@' in proxy else f'http://{_proxy[2]}:{_proxy[3]}@{_proxy[0]}:{_proxy[1]}', 'https://': _proxy if '@' in proxy else f'http://{_proxy[2]}:{_proxy[3]}@{_proxy[0]}:{_proxy[1]}'} if proxy else None

	data_dict_b['mode'] = [x for x in data_dict['mode'] if data_dict['mode'][x]][0] if len([x for x in data_dict['mode'] if data_dict['mode'][x]]) > 0 else ''
	data_dict_b['check_mode'] = [{'Каналы': InputPeerChannel, 'Чаты': InputPeerChat, 'Личные сообщения': InputPeerUser}[x] for x in data_dict['check_mode'] if data_dict['check_mode'][x]]
update_b()


logging.info(f'Запуск скрипта\n\nКоличество сессий: {len(data_dict_b["accounts"])}\nСтроки для заполнения:\n\tЛичный канал [{data_dict["to_change"]["self_channel"]}]\n\tАватарки [{data_dict["to_change"]["avatar"]}]: {len(data_dict_b["avatars"])}\n\tАватарки для личного канала [{data_dict["to_change"]["self_channel"]}]: {len(data_dict_b["self_channel_avatars"])}\n\tФамилии [{data_dict["to_change"]["name_surname"]}]: {len(data_dict_b["surnames"])}\n\tИмена [{data_dict["to_change"]["name_surname"]}]: {len(data_dict_b["names"])}\n\tБио [{data_dict["to_change"]["bio"]}]: {len(data_dict_b["bios"])}\n\tАвтовступление [{data_dict["to_change"]["auto_join_ft"]}]: {len(data_dict_b["bios"])}\n\n\n\n')

async def proxy_check():
	async with httpx.AsyncClient(proxies=data_dict_b['proxies']) as client:
		try:
			if (await client.get('http://ip.bablosoft.com')).status_code == 407: raise httpx.ProxyError('Хуйня прокси')
		except Exception as error:
			logging.critical('Невалидные прокси, завершаю скрипт...')

async def send_msg(text: str):
	async with httpx.AsyncClient() as aclient:
		try: await aclient.post(f'https://api.telegram.org/bot{data_dict["bot_token"]}/sendMessage', json={'chat_id': data_dict["notify_user_id"], 'text': text, 'parse_mode': 'HTML', 'reply_markup': {'inline_keyboard': [ [{ 'text': '❌ Закрыть', 'callback_data': 'utils:close' }] ]}})
		except: ...
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
					if True not in [isinstance(dialog.input_entity, x) for x in data_dict_b['check_mode']]: continue # Проверка по check_mode

					if len(self._spam_channels) > 0:
						if True not in [x in (dialog.name, dialog.entity.id) for x in self._spam_channels]: continue # Проверка на цель "где искать посты"

						target = dialog.entity.id
						text = data_dict['channels|dm']['default_message']
						try: text = self._spam_channels[target] if self._spam_channels[target] else data_dict['channels|dm']['default_message']
						except: pass

						self.spam_channels[target] = text
					else:
						target = dialog.entity.id
						text = data_dict['channels|dm']['default_message']

						self.spam_channels[target] = text


				logging.info(f'Количество целей: {len(self.spam_channels)}')
				logging.debug(f'Полученые id целей:\n{json.dumps(self.spam_channels, indent=4)}')
			
			case 'stories':
				async for dialog in self.client.iter_dialogs(): #InputPeerChannel, InputPeerSelf, InputPeerUser, InputPeerChat
					if True not in [isinstance(dialog.input_entity, x) for x in data_dict_b['check_mode']]: continue # Проверка по check_mode

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

					if True not in [isinstance(dialog.input_entity, x) for x in data_dict_b['check_mode']]: continue # Проверка по check_mode
					if len(self._parse_chats) > 0:
						if True not in [x in (dialog.name, dialog.entity.id) for x in self._parse_chats]: continue # Проверка на цель "откуда приглашать"


					self.parse_chats.append(dialog.entity.id)


				logging.info(f'Количество целей [откуда]: {len(self.parse_chats)}')
				logging.info(f'Количество целей [куда]: {len(self.parse_invites)}')
				logging.debug(f'Полученые id целей [откуда]:\n{json.dumps(self.parse_chats, indent=4)}')
				logging.debug(f'Полученые id целей [куда]:\n{json.dumps(self.parse_invites, indent=4)}')


##############################################################################
async def os_remove(session_path, session_file):
	await asyncio.sleep(5)
	await aiofiles.os.makedirs(data_dict["path_sessions_spamblock"], exist_ok=True)
	await aiofiles.os.replace(session_path, f'{data_dict["path_sessions_spamblock"]}/{session_file}')

async def on_new_message(client, session, user, e) -> None:
	session_path, session_file = session[0], session[1]
	await asyncio.sleep(3)
	message = e.message
	words_count = len(message.message.split(' '))

	if words_count < 20:
		logging.info(f'[{session_file.replace(".session", "")}] Спам блок не найден')
		if data_dict['spam_block']['notify']:
			await send_msg(f'<b>🔓 Спам блока нет</b>\nАккаунт: {user}\n\n<i>Спам блок не найден</i>')
	else:
		logging.info(f'[{session_file.replace(".session", "")}] Спам блок подтвержден')
		if data_dict['spam_block']['notify']:
			await send_msg(f'<b>🔒 Спам блока найден</b>\nАккаунт: {user}\n\n<i>Спам блок подтвержден</i>')
		
		if data_dict['spam_block']['replace_session']:
			asyncio.get_event_loop().create_task(os_remove(session_path, session_file))
			await client.disconnect()

async def check_spamblock(client):
	try:
		result = await client.send_message('SpamBot', '/start')
		return 1
	except: ...
	return 0


async def spam_block_check():
	clients = list(data_dict['telethon_clients'])
	tasks = []
	for client in clients:
		task = check_spamblock(client)
		tasks.append(task)
	v = sum(await asyncio.gather(*tasks))
	return v


async def auto_join(client):
	for target in dict(data_dict_b['auto_join_channels']):
		try:
			try: await client(JoinChannelRequest(target))
			except: await client(ImportChatInviteRequest(target.replace('+', '').replace('https://t.me/', '')))
			logging.info(f'[auto_join] Успешно присоединился к {target}')
			await asyncio.sleep(random.randint(600, 1200))
		except Exception as e:
			logging.info(f'[auto_join] Не удалось присоединиться к {target}: {e}')






async def main_channels(session):
	session, session_name = session
	client = TelegramClient(session, 69696969, 'qwertyuiopasdfghjklzxcvbnm1234567', flood_sleep_threshold=120, system_lang_code='en', system_version='4.16.30-vxCUSTOM', proxy=(socks.HTTP, data_dict_b['_proxy'][0], int(data_dict_b['_proxy'][1]), True, data_dict_b['_proxy'][2], data_dict_b['_proxy'][3]) if data_dict['proxy'] else None)
	data_dict['telethon_clients'].append(client)
	await client.start()
	if data_dict['to_change']['auto_join_ft']:
		asyncio.get_event_loop().create_task(auto_join(client))
	me = await client.get_me()
	user = f'@{me.username} (<code>{me.id}</code>)' if me.username else f'<code>{me.id}</code>'
	client.add_event_handler(lambda e: on_new_message(client, (session, session_name), user, e), events.NewMessage(incoming=True, outgoing=False, from_users=[178220800]))

	data = client_parser(client, data_dict_b['mode'], spam_channels=data_dict['channels|dm']['spam_channels'])
	await data.sync_channels()


	@client.on(events.NewMessage(chats=data.spam_channels))
	async def message_handler(event):
		message = event.message
		try:
			channel_id = message.peer_id.channel_id; 
			if (not message.replies.comments) or (not message.post): return
		except AttributeError: return
		except Exception as error: return logging.error(f'[{session_name}] Ошибка при получении объекта [{message.peer_id}]: {error}')
		

		if data_dict['channels|dm']['generate_text'] and data_dict['channels|dm']['openai_api_key']:
			try:
				async with httpx.AsyncClient(proxies=data_dict_b['proxies']) as aclient:
					req = (await aclient.post('https://api.openai.com/v1/chat/completions', headers={'Content-Type':'application/json','Authorization': f"Bearer {data_dict['channels|dm']['openai_api_key']}"}, json={'model':'gpt-3.5','messages': [*data_dict['channels|dm']['gpt_dialog_story'], {"role": "user", "content": f"Придумай осмысленный человекоподобный комментарий, до 11 слов к посту: {message.message}"}], 'temperature': 0.7})).json()
				if 'choices' in req: text = req['choices'][0]['message']['content'].strip()
				else: text = random.choice(data_dict['channels|dm']['gpt_not_working_answer_variants'])

				if len(text) == 0: text = random.choice(data_dict['channels|dm']['gpt_not_working_answer_variants'])
			except Exception as e:
				logging.error(f'[{session_name} | LINE:{traceback.extract_tb(e.__traceback__)[-1].lineno}] Не удалось сгенерировать комментарий ({type(e)}): {e}\n{traceback.format_exc()}')
				text = random.choice(data_dict['channels|dm']['gpt_not_working_answer_variants'])
		else:
			text = data.spam_channels[channel_id] if isinstance(data.spam_channels[channel_id], str) else random.choice(data.spam_channels[channel_id])
		try:
			await asyncio.sleep(random.randint(*data_dict['channels|dm']['time_before_message']))
			if isinstance(text, dict): await client.send_file(channel_id, Document(id=text['id'], access_hash=text['access_hash'], file_reference=b'\x00f\xab\xbf\xa9:{\x10\xa8\xcc\x9aO\xc9(\xd6\xe2\xfc\xf7\xdd\xa0T', date=datetime(2018, 12, 23, 3, 40, 1, tzinfo=timezone.utc), mime_type='image/webp', size=0, dc_id=5, attributes=[], thumbs=[], video_thumbs=[]), comment_to=message.id)
			else: await client.send_message(entity=channel_id, message=text, comment_to=message.id)
			logging.info(f'[{session_name}] Прокомментировал пост')
		except common.TypeNotFoundError:
			result = None
			if data_dict['spam_block']['advanced_check']:
				logging.info(f'[{session_name}] Начинаю проверку на спам блок')
				try: result = await client.send_message('SpamBot', '/start')
				except: ...
			if data_dict['spam_block']['notify']:
				await send_msg(f'<b>🔒 Обнаружен возможный Спам блок</b>\nАккаунт: {user}\n\n{"<i>Началась проверка аккаунта на спам блок</i>" if result else "<i>Не удалось проверить аккаунт на спам блок</i>"}')
		except Exception as error:
			logging.error(f'[{session_name} | LINE:{traceback.extract_tb(error.__traceback__)[-1].lineno}] Ошибка при отправке комментария: {error}')



	await client.start()
	if data_dict['to_change']['auto_join_ft']:
		asyncio.get_event_loop().create_task(auto_join(client))
	try: await client.run_until_disconnected()
	except: await client.disconnect()



async def main_dm(session):
	session, session_name = session
	client = TelegramClient(session, 69696969, 'qwertyuiopasdfghjklzxcvbnm1234567', flood_sleep_threshold=120, system_lang_code='en', system_version='4.16.30-vxCUSTOM', proxy=(socks.HTTP, data_dict_b['_proxy'][0], int(data_dict_b['_proxy'][1]), True, data_dict_b['_proxy'][2], data_dict_b['_proxy'][3]) if data_dict['proxy'] else None)
	data_dict['telethon_clients'].append(client)
	await client.start()
	if data_dict['to_change']['auto_join_ft']:
		asyncio.get_event_loop().create_task(auto_join(client))
	me = await client.get_me()
	user = f'@{me.username} (<code>{me.id}</code>)' if me.username else f'<code>{me.id}</code>'
	client.add_event_handler(lambda e: on_new_message(client, (session, session_name), user, e), events.NewMessage(incoming=True, outgoing=False, from_users=[178220800]))


	data = client_parser(client, data_dict_b['mode'], spam_channels=data_dict['channels|dm']['spam_channels'])
	await data.sync_channels()

	count = 0
	logging.info(f'[{session_name}] Начинаю писать людям...\n\n')
	try:
		for entity in [await client.get_entity(x) for x in data.spam_channels]:
			try:
				users = await client.get_participants(entity.id)
			except telethon.errors.rpcerrorlist.ChatAdminRequiredError: continue
			except Exception as error:
				logging.error(f'[{session_name}] Не удалось получить участников [{entity.id}]: {error}')
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
	except common.TypeNotFoundError:
		result = None
		if data_dict['spam_block']['advanced_check']:
			logging.info(f'[{session_name}] Начинаю проверку на спам блок')
			try: result = await client.send_message('SpamBot', '/start')
			except: ...
		if data_dict['spam_block']['notify']:
			await send_msg(f'<b>🔒 Обнаружен возможный Спам блок</b>\nАккаунт: {user}\n\n{"<i>Началась проверка аккаунта на спам блок</i>" if result else "<i>Не удалось проверить аккаунт на спам блок</i>"}')
	except Exception as error: logging.error(f'[{session_name}] Глобальная ошибка: {error}')


	await client.disconnect()
	logging.info(f'[{session_name}] Работа скрипта завершена\nВсего отправлено сообщений: {count}')


async def main_stories(session):
	session, session_name = session
	client = TelegramClient(session, 69696969, 'qwertyuiopasdfghjklzxcvbnm1234567', flood_sleep_threshold=120, system_lang_code='en', system_version='4.16.30-vxCUSTOM', proxy=(socks.HTTP, data_dict_b['_proxy'][0], int(data_dict_b['_proxy'][1]), True, data_dict_b['_proxy'][2], data_dict_b['_proxy'][3]) if data_dict['proxy'] else None)
	data_dict['telethon_clients'].append(client)
	await client.start()
	if data_dict['to_change']['auto_join_ft']:
		asyncio.get_event_loop().create_task(auto_join(client))
	me = await client.get_me()
	user = f'@{me.username} (<code>{me.id}</code>)' if me.username else f'<code>{me.id}</code>'
	client.add_event_handler(lambda e: on_new_message(client, (session, session_name), user, e), events.NewMessage(incoming=True, outgoing=False, from_users=[178220800]))

	data = client_parser(client, data_dict_b['mode'], parse_chats=data_dict[data_dict_b['mode']]['parse_chats'])
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
		except common.TypeNotFoundError:
			result = None
			if data_dict['spam_block']['advanced_check']:
				logging.info(f'[{session_name}] Начинаю проверку на спам блок')
				try: result = await client.send_message('SpamBot', '/start')
				except: ...
			if data_dict['spam_block']['notify']:
				await send_msg(f'<b>🔒 Обнаружен возможный Спам блок</b>\nАккаунт: {user}\n\n{"<i>Началась проверка аккаунта на спам блок</i>" if result else "<i>Не удалось проверить аккаунт на спам блок</i>"}')
		except Exception as e: logging.error(f'[{session_name}] Ошибка при получении чата или участников чата [{target.id}]: {e}')
	
	await client.disconnect()
	logging.info(f'[{session_name}] Работа скрипта завершена\nВсего просмотрено историй: {valid}')


async def main_invite(session):
	session, session_name = session
	client = TelegramClient(session, 69696969, 'qwertyuiopasdfghjklzxcvbnm1234567', flood_sleep_threshold=120, system_lang_code='en', system_version='4.16.30-vxCUSTOM', proxy=(socks.HTTP, data_dict_b['_proxy'][0], int(data_dict_b['_proxy'][1]), True, data_dict_b['_proxy'][2], data_dict_b['_proxy'][3]) if data_dict['proxy'] else None)
	data_dict['telethon_clients'].append(client)
	await client.start()
	if data_dict['to_change']['auto_join_ft']:
		asyncio.get_event_loop().create_task(auto_join(client))
	me = await client.get_me()
	user = f'@{me.username} (<code>{me.id}</code>)' if me.username else f'<code>{me.id}</code>'
	client.add_event_handler(lambda e: on_new_message(client, (session, session_name), user, e), events.NewMessage(incoming=True, outgoing=False, from_users=[178220800]))

	data = client_parser(client, data_dict_b['mode'], parse_chats=data_dict[data_dict_b['mode']]['parse_chats'], parse_invites=data_dict[data_dict_b['mode']]['parse_invites'])
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
					except telethon.errors.rpcerrorlist.PeerFloodError: logging.info(f"[{session_name}] Ошибка от телеграма: флуд")
					except telethon.errors.rpcerrorlist.UserPrivacyRestrictedError: pass
					except Exception as e: logging.error(f'[{session_name}] Ошибка при отправке приглашения: {e}')
			except (telethon.errors.rpcerrorlist.UsernameInvalidError, telethon.errors.rpcerrorlist.UsernameNotOccupiedError, telethon.errors.rpcbaseerrors.BadRequestError): pass
			except common.TypeNotFoundError:
				result = None
				if data_dict['spam_block']['advanced_check']:
					logging.info(f'[{session_name}] Начинаю проверку на спам блок')
					try: result = await client.send_message('SpamBot', '/start')
					except: ...
				if data_dict['spam_block']['notify']:
					await send_msg(f'<b>🔒 Обнаружен возможный Спам блок</b>\nАккаунт: {user}\n\n{"<i>Началась проверка аккаунта на спам блок</i>" if result else "<i>Не удалось проверить аккаунт на спам блок</i>"}')
			except Exception as e: logging.error(f'[{session_name}] Ошибка при получении чата или участников чата [{target.id}]: {e}')
	
	await client.disconnect()
	logging.info(f'[{session_name}] Работа скрипта завершена')




async def prepare_session(session):
	session, session_name = session
	try: client = TelegramClient(session, 69696969, 'qwertyuiopasdfghjklzxcvbnm1234567', flood_sleep_threshold=120, system_lang_code='en', system_version='4.16.30-vxCUSTOM', proxy=(socks.HTTP, data_dict_b['_proxy'][0], int(data_dict_b['_proxy'][1]), True, data_dict_b['_proxy'][2], data_dict_b['_proxy'][3]) if data_dict['proxy'] else None)
	except Exception as e:
		logging.info(f'[{session_name}] Ошибка создание объекта аккаунта: {e}\n\n')
		return (session, False)

	logging.info(f'[{session_name}] Подключаюсь к сессии.')
	try: await client.connect()
	except ConnectionError:	
		logging.info(f'[{session_name}] Ошибка подключения к сессии, беру другой аккаунт\n\n')
		await client.disconnect()
		return (session, False)
	except rpcerrorlist.FloodWaitError: 
		logging.info(f'[{session_name}] Лимит авторизаций, беру другой аккаунт\n\n')
		await client.disconnect()
		return (session, False)
	except Exception as e:
		logging.info(f'[{session_name}] Ошибка подключения аккаунта: {e}\n\n')
		await client.disconnect()
		return (session, False)
	if not await client.is_user_authorized(): 
		await send_msg(f"<b>💀 Мертвая сессия</b>\n├ <i>Файл сессии:</i>  <code>{session}</code>")
		logging.info(f'[{session_name}] Мертвая сессия, беру другую\n\n')
		await client.disconnect()
		return (session, False)
	else: logging.info(f'[{session_name}] Успешно подключился к сессии\n')

	if data_dict['to_delete']['previous_avatars']:
		user = await client.get_me()
		photos = await client(GetUserPhotosRequest(user_id=user.id, offset=0, max_id=0, limit=100))
		input_photos = [InputPhoto(id=photo.id, access_hash=photo.access_hash, file_reference=photo.file_reference) for photo in photos.photos]
		if input_photos:
			await client(DeletePhotosRequest(id=input_photos))
			logging.info(f'[{session_name}] Удалено {len(input_photos)} аватарок')
		else:
			logging.info(f'[{session_name}] Нет аватарок для удаления')

	if data_dict['to_delete']['chatlists']:
		this_filters = await client(GetDialogFiltersRequest())
		v = 0
		nv = len(this_filters.filters)
		for filter in this_filters.filters:
			try:
				await client(LeaveChatlistRequest(chatlist=InputChatlistDialogFilter(filter_id=filter.id), peers=[]))
				v += 1
			except: ...
		logging.info(f'[{session_name}] Удалено {v} из {nv} чатлистов')



	if data_dict['to_change']['chatlists']:
		for x in open(data_dict['path_chatlists'], 'r', encoding='utf-8').read().splitlines():
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
				else: logging.info(f'[{session_name}] Не удалось проверить чатлист: {e}')
	
	if data_dict['to_change']['name_surname'] and (len(data_dict_b['names']) > 0 or len(data_dict_b['surnames']) > 0):
		name, surname = random.choice(data_dict_b['names']) if len(data_dict_b['names']) else '', random.choice(data_dict_b['surnames']) if len(data_dict_b['surnames']) else ''
		logging.info(f'[{session_name}] Устанавливаю имя и фамилию: "{name} {surname}"')
		try:
			await client(UpdateProfileRequest(first_name=name, last_name=surname))
			logging.info(f'[{session_name}] Имя и Фамилия успешно установлены')
		except Exception as e: logging.error(f'[{session_name}] Не удалось установить имя и фамилию. Ошибка: {e}')
	
	if data_dict['to_change']['bio'] and len(data_dict_b['bios']) > 0:
		bio = random.choice(data_dict_b['bios'])
		logging.info(f'[{session_name}] Устанавливаю био: {bio}')
		try:
			await client(UpdateProfileRequest(about=bio))
			logging.info(f'[{session_name}] Био успешно установлено')
		except Exception as e: logging.error(f'[{session_name}] Не удалось био. Ошибка: {e}')
	
	if data_dict['to_change']['avatar'] and len(data_dict_b['avatars']) > 0:
		avatar = random.choice(data_dict_b['avatars'])
		logging.info(f'[{session_name}] Устанавливаю аватарку: {avatar}')
		try: 
			await client(UploadProfilePhotoRequest(file=await client.upload_file(avatar)))
			logging.info(f'[{session_name}] Аватарка успешно установлена')
		except Exception as e: logging.error(f'[{session_name}] Не удалось установить аватарку. Ошибка: {e}')
	
	if data_dict['to_change']['self_channel']:
		channel = None
		for x in range(3):
			try:
				channel_username = ''.join(random.choices(data_dict['self_channel']['username']['symbols'], k=data_dict['self_channel']['username']['length']))
				result = await client(CreateChannelRequest(title=data_dict['self_channel']['title'], about=data_dict['self_channel']['about'], megagroup=False))
				channel = result.chats[0]
				await client(UpdateUsernameRequest(channel, channel_username))
				if data_dict['self_channel']['avatar']:
					if len(data_dict_b['self_channel_avatars']) == 0:
						logging.info(f'[{session_name}] Нет доступных аватарок для канала: @{channel_username}')
					else:
						await client(EditPhotoRequest(channel=channel, photo=await client.upload_file(random.choice(data_dict_b['self_channel_avatars']))))
						logging.info(f'[{session_name}] Аватарка для канала успешно установлена')
				messages = [message.id for message in await client.get_messages(channel)]
				result = await client(functions.channels.DeleteMessagesRequest(channel=channel, id=messages))
				if data_dict['self_channel']['forward_enabled']:
					await client(ForwardMessagesRequest(from_peer=data_dict['self_channel']['forward_from_username'], id=[data_dict['self_channel']['forward_from_message_id']], to_peer=channel, silent=False, background=False, with_my_score=False, drop_author=True))
				break
			except Exception as e:
				if "You're admin of too many public channels, make some channels" in str(e):
					logging.info(f'[{session_name}] Не удалось личный канал. Ошибка: {str(e)}')
					break
				logging.error(f'self_channel {str(e)}')
		if channel:
			logging.info(f'[{session_name}] Устанавливаю личный канал: @{channel_username}')
			try:
				result = await client(UpdatePersonalChannelRequest(channel=channel))
			except Exception as e: logging.error(f'[{session_name}] Не удалось личный канал. Ошибка: {e}')
			logging.info(f'[{session_name}] Личный канал успешно установлен')
	
	if data_dict['to_change']['disable_notify']:
		dialogs = await client.get_dialogs()
		v = 0
		nv = 0
		for dialog in dialogs:
			if dialog.is_channel or dialog.is_group:
				nv += 1
				try:
					settings = InputPeerNotifySettings(show_previews=False, silent=True, mute_until=2**31-1)
					result = await client(UpdateNotifySettingsRequest(peer=InputNotifyPeer(dialog.entity), settings=settings))
					v += 1
				except: ...
		logging.info(f'[{session_name}] Выключены уведомления в {v} из {nv} каналах')
	
	if data_dict['to_change']['privacy_settings']:
		await client(functions.account.SetPrivacyRequest(key=InputPrivacyKeyAbout(), rules=[InputPrivacyValueAllowAll()]))
		await client(functions.account.SetPrivacyRequest(key=InputPrivacyKeyProfilePhoto(), rules=[InputPrivacyValueAllowAll()]))
		logging.info(f'[{session_name}] Включено отображение био и фото для всех')

	await client.disconnect()
	return (session, True)

##############################################################################



async def main():
	data_dict['telethon_clients'] = []
	future = asyncio.create_task(tg_bot_func(data_dict, update_b, spam_block_check))
	await proxy_check()

	match data_dict_b['mode']:
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
		
		sessions = await run_instances(prepare_session, data_dict_b['accounts'])
		logging.info('Данные на аккаунтах обновлены, запускаю текущий режим\n\n')
		await run_instances(target, sessions)
	else: logging.info('Вы не выбрали режим работы')
	await future

if __name__ == '__main__':
	asyncio.run(main())