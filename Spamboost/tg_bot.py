import aiofiles.os, aiofiles, asyncio, logging, sqlite3, zipfile, shutil, random, json, sys, ast, os

from aiogram import Bot, Dispatcher, Router, F, html
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton, KeyboardButton, FSInputFile
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.filters import StateFilter
from aiogram.enums import ParseMode, ContentType
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import *

t = {
	'path_sessions':	'Сессии',
	'path_sessions_spamblock':	'Спам блок',
	'path_avatars':		'Аватарки',
	'path_channels_avatars':	'Аватарки Канала',
	'path_names':		'Имена',
	'path_surnames':	'Фамилии',
	'path_bio':			'Био',
	'path_chatlists':	'Чатлисты',
	'path_auto_join':	'Каналы Автовхода',
	'bot_token':		'Токен бота',
	'notify_user_id':	'ID для уведомлений',
	'admin_ids':		'ID админов',
	'proxy':			'Прокси',

	'mode':				'Режим работы',
	'check_mode':		'Типы целей',
	'to_change':		'Изменения аккаунта',
	'to_delete':		'Удаление с аккаунта',
	'self_channel':		'Личный канал',
	
	'spam_block':		'Спам блок',
	'notify':			'Уведомление',
	'advanced_check':	'Автопроверка через бота',
	'replace_session':	'Перемещение сессий',

	'dm':				'Режим "Лс"',
	'channels':			'Режим "Каналы"',
	'channels|dm':		'Режим "Каналы\\лс"',
	'generate_text':	'Генерировать текст',
	'openai_api_key':	'Ключ OpenAI',
	'gpt_dialog_story':	'История чатгпт',
	'gpt_not_working_answer_variants':	'Ответы при ошибке',
	'time_before_message':	'Время перед отправкой',
	'default_message':	'Текст для спама',
	'spam_channels':	'Каналы для спама',

	'stories':			'Режим "Истории"',
	'parse_chats':		'Откуда парсить',
	'enable_likes':		'Лайкать истории',

	'invite_to':		'Режим "Приглашение"',
	'parse_invites':	'Куда приглашать',
	'parse_chats':		'Откуда парсить',

	'avatar':			'Аватар',
	'name_surname':		'Имя и Фамилия',
	'bio':				'Поле "О себе"',
	'chatlists':		'Чатлисты',
	'disable_notify':	'Выключить уведомления',
	'auto_join_ft':		'Автовступление в каналы из .txt',
	'privacy_settings':	'Настройки конфиденциальности',
	'previous_avatars':	'Предыдущие аватарки',

	'title':			'Название',
	'about':			'Описание',
	'enabled':			'Включено',
	'path_to_folder':	'Путь до папки',
	'username':			'Юзернейм',
	'length':			'Длина',
	'symbols':			'Символы',
	'forward_enabled':			'Пересылка',
	'forward_from_username':	'Username от кого пересылать',
	'forward_from_message_id':	'ID сообщения для пересылки',
}
#################################################################################################################################
def ikb_construct(*buttons, back_button=None, keyboard=None) -> InlineKeyboardBuilder:
	if not keyboard:
		keyboard = InlineKeyboardBuilder()

	for row in buttons:
		keyboard.row(*row)
	if back_button:
		keyboard.row(back_button)
	return keyboard.as_markup()

# Генерация инлайн кнопки
def ikb(text: str, data: str = None, url: str = None) -> InlineKeyboardButton:
	if data is not None:
		return InlineKeyboardButton(text=text, callback_data=data)
	elif url is not None:
		return InlineKeyboardButton(text=text, url=url)


def kb_delete():
	return ikb_construct([
		ikb('❌ Закрыть', data='utils:close')
	])

def kb_main_menu():
	return ikb_construct(
		[ikb('Расходники', data='utils:menu:sup'), ikb('Настройки скрипта', data='utils:menu:cfg')],
		[ikb('❗️ Перезапустить скрипт', data='utils:restart')]
	)

def kb_sup_menu(q: str = None):
	if q is None:
		s = [
			['path_sessions', 'path_sessions_spamblock'],
			['path_avatars', 'path_channels_avatars'],
			['path_names', 'path_surnames', 'path_bio'],
			['path_chatlists', 'path_auto_join'],
			['proxy', 'bot_token'],
			['admin_ids', 'notify_user_id']
		]
		return ikb_construct(*[
			[ikb(t.get(x, x), data=f'utils:sub_menu:{x}') for x in z] for z in s
		], back_button=ikb('↪ Назад', data=f'utils:menu:main'))
	
	elif q in ['path_sessions_spamblock']:
		s = [
			{'🗑 Удалить все файлы': 'delete'},
			{'🚀 Получить данные': 'get'},
			{'↪ Назад': f'utils:menu:sup'}
		]
		return ikb_construct(*[
			[ikb(x[0], data=x[1] if ':' in x[1] else f'utils:change:{q}:{x[1]}') for x in z.items()] for z in s
		])
	
	elif q in ['path_sessions', 'path_avatars', 'path_channels_avatars']:
		s = [
			{'✏️ Добавить': 'add', '🗑 Удалить все файлы': 'delete'},
			{'🚀 Получить данные': 'get'},
			{'↪ Назад': f'utils:menu:sup'}
		]
		return ikb_construct(*[
			[ikb(x[0], data=x[1] if ':' in x[1] else f'utils:change:{q}:{x[1]}') for x in z.items()] for z in s
		])
	
	elif q in ['path_names', 'path_surnames', 'path_bio', 'path_chatlists', 'path_auto_join']:
		s = [
			{'✏️ Добавить': 'add', '🗑 Очистить файл': 'delete'},
			{'🚀 Получить файл': 'get'},
			{'↪ Назад': f'utils:menu:sup'}
		]
		return ikb_construct(*[
			[ikb(x[0], data=x[1] if ':' in x[1] else f'utils:change:{q}:{x[1]}') for x in z.items()] for z in s
		])
	
	elif q in ['bot_token', 'notify_user_id', 'admin_ids', 'proxy']:
		s = [
			{'✏️ Изменить': 'edit'},
			{'↪ Назад': f'utils:menu:sup'}
		]
		return ikb_construct(*[
			[ikb(x[0], data=x[1] if ':' in x[1] else f'utils:change:{q}:{x[1]}') for x in z.items()] for z in s
		])
	elif q in ['bback']:
		return ikb_construct(*[], back_button=ikb('↪ Назад', data='utils:menu:sup'))
	else:
		s = [
			{'↪ Назад': f'utils:menu:sup'}
		]
		return ikb_construct(*[
			[ikb(x[0], data=x[1] if ':' in x[1] else f'utils:change:{q}:{x[1]}') for x in z.items()] for z in s
		])


def kb_cfg_menu(sub_menu: str = None, q: str = None):
	if not sub_menu:
		s = [
			['mode', 'check_mode'],
			['to_change', 'to_delete'],
			['spam_block'],
			['self_channel'],
			['channels|dm'],
			['stories'],
			['invite_to']
		]
		return ikb_construct(*[
			[ikb(t.get(x, x), data=f'utils:cfg_menu:{x}') for x in z] for z in s
		], back_button=ikb('↪ Назад', data=f'utils:menu:main'))
	
	elif q in ['bback']:
		return ikb_construct(*[], back_button=ikb('↪ Назад', data=f'utils:cfg_menu:{sub_menu}'))


	elif sub_menu in ['channels|dm', 'stories', 'invite_to', 'self_channel'] and q in ['generate_text', 'openai_api_key', 'gpt_dialog_story', 'gpt_not_working_answer_variants', 'time_before_message', 'default_message', 'spam_channels', 'parse_chats', 'enable_likes', 'parse_invites', 'parse_chats', 'name_surname', 'bio', 'chatlists', 'disable_notify', 'auto_join_ft', 'privacy_settings', 'previous_avatars', 'title', 'about', 'path_to_folder', 'username', 'length', 'symbols', 'forward_from_username', 'forward_from_message_id']:
		s = [
			{'✏️ Изменить': 'edit'}
		]
		return ikb_construct(*[
			[ikb(x[0], data=x[1] if ':' in x[1] else f'utils:change_:{sub_menu}:{q}:{x[1]}') for x in z.items()] for z in s
		], back_button=ikb('↪ Назад', data=f'utils:cfg_menu:{sub_menu}'))

	
	elif sub_menu in ['channels|dm', 'stories', 'invite_to', 'self_channel']:
		s = [
			{f'{"🟢" if x[1] else "🔴"} {t.get(x[0], x[0])}': f'{x[0]}${not x[1]}'} if x[0] in ['generate_text', 'enable_likes', 'forward_enabled', 'avatar'] else {t.get(x[0], x[0]): x[0]} for x in _data_dict[sub_menu].items() if x[0] not in ['username']
		]
		return ikb_construct(*[
			[ikb(x[0], data=x[1] if ':' in x[1] else f'utils:change_:{sub_menu}:{x[1]}') for x in z.items()] for z in s
		], back_button=ikb('↪ Назад', data='utils:menu:cfg'))
	
	elif sub_menu in ['mode', 'check_mode', 'to_change', 'to_delete', 'spam_block']:
		s = [
			{f'{"🟢" if x[1] else "🔴"} {t.get(x[0], x[0])}': f'{x[0]}${not x[1]}'} for x in _data_dict[sub_menu].items()
		]
		if sub_menu in ['spam_block']:
			s.append({'🔍 Проверить все аккаунты': 'utils:check_spamblock'})
		return ikb_construct(*[
			[ikb(x[0], data=x[1] if ':' in x[1] else f'utils:change_:{sub_menu}:{x[1]}') for x in z.items()] for z in s
		], back_button=ikb('↪ Назад', data='utils:menu:cfg'))

	else:
		s = [
			{'↪ Назад': f'utils:menu:cfg'}
		]
		return ikb_construct(*[
			[ikb(x[0], data=x[1] if ':' in x[1] else f'utils:change_:{q}:{x[1]}') for x in z.items()] for z in s
		])


main_router = Router()
bot = Bot(token=data_dict['bot_token'], default=DefaultBotProperties(parse_mode=ParseMode.HTML))

class states(StatesGroup):
	change_smth = State()
	change_smth_ = State()


async def delmsg(*msgs):
	for x in msgs:
		try: await x.delete()
		except: ...
#################################################################################################################################


async def send_files_as_zip(call, folder_path):
	TELEGRAM_FILE_LIMIT = 50 * 1024 * 1024  # 50 MB
	try:
		files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
		if not files:
			await call.answer('Папка пустая', show_alert=True)
			return
		
		zip_files = []
		zip_index = 1
		current_zip_path = os.path.join(folder_path, f'archive_{zip_index}.zip')
		current_zip = zipfile.ZipFile(current_zip_path, 'w')
		current_zip_size = 0

		for file in files:
			file_size = os.path.getsize(file)
			if current_zip_size + file_size > TELEGRAM_FILE_LIMIT:
				current_zip.close()
				zip_files.append(current_zip_path)
				zip_index += 1
				current_zip_path = os.path.join(folder_path, f'archive_{zip_index}.zip')
				current_zip = zipfile.ZipFile(current_zip_path, 'w')
				current_zip_size = 0
			
			current_zip.write(file, os.path.basename(file))
			current_zip_size += file_size

		current_zip.close()
		zip_files.append(current_zip_path)

		for zip_file in zip_files:
			await call.message.answer_document(FSInputFile(zip_file), reply_markup=kb_delete())
			await aiofiles.os.remove(zip_file)
		
		await call.answer()
	
	except Exception as e:
		print(f"Error: {e}")
		await call.answer(f'Произошла ошибка при упаковке файлов: {e}', show_alert=True)




@main_router.callback_query(F.data.startswith('utils'), StateFilter('*'))
async def handler_utils(call: CallbackQuery, state: FSMContext):
	if call.from_user.id not in _data_dict['admin_ids']: return
	await state.clear()
	cd = call.data.split(':')

	if cd[1] == 'restart':
		await call.answer('🚀 Скрипт и бот перезапускаются.\nБот будет доступен в течении 15 секунд', show_alert=True)
		exit('restart')

	elif cd[1] == 'check_spamblock':
		v = await spam_block_check()
		await call.answer(f'🚀 Проверка на спамблок запущена на {v} аккаунтах', show_alert=True)

	elif cd[1] == 'menu':
		menu = cd[2]
		if menu == 'main':
			await call.message.edit_text(f'<b>⚙️ Выберите что изменить</b>', reply_markup=kb_main_menu())
		elif menu == 'sup':
			await call.message.edit_text(f'<b>⚙️ Выберите элемент</b>', reply_markup=kb_sup_menu())
		elif menu == 'cfg':
			await call.message.edit_text(f'<b>⚙️ Выберите элемент</b>', reply_markup=kb_cfg_menu())
		else:
			await call.answer('Неизвестное меню')

	elif cd[1] == 'sub_menu':
		q = cd[2]
		z = f'\nТекущее значение: <code>{_data_dict[q]}</code>' if q in ['bot_token', 'notify_user_id', 'proxy', 'admin_ids'] else ''
		await call.message.edit_text(f'<b>⚙️ Выберите действие для <i>{t.get(q, q)}</i>{z}</b>', reply_markup=kb_sup_menu(q))

	elif cd[1] == 'cfg_menu':
		sub_menu = cd[2]
		await call.message.edit_text(f'<b>⚙️ Что изменить в <i>{t.get(sub_menu, sub_menu)}</i></b>', reply_markup=kb_cfg_menu(sub_menu))
		

	elif cd[1] == 'change':
		sub_menu = cd[2]
		q = cd[3]

		if q == 'add':
			msg = await call.message.edit_text(f"<b>Отправьте {'текст' if sub_menu in ['path_names', 'path_surnames', 'path_bio', 'path_chatlists', 'path_auto_join'] else 'файл' if sub_menu in ['path_sessions'] else 'фото'}</b>", reply_markup=kb_sup_menu('bback'))
			await state.set_state(states.change_smth)
			await state.update_data(sub_menu=sub_menu, msg=msg)

		elif q == 'delete':
			if sub_menu in ['path_sessions', 'path_sessions_spamblock', 'path_avatars', 'path_channels_avatars']:
				if sub_menu in ['path_sessions']:
					for x in _data_dict['telethon_clients']:
						try: await x.disconnect()
						except Exception as e: logging.error(f'disconnect_session, {e}')
					await asyncio.sleep(1)
				files = os.listdir(_data_dict[sub_menu])
				v = 0
				for x in files:
					try:
						await aiofiles.os.remove(f"{_data_dict[sub_menu]}/{x}")
						v += 1
					except Exception as e: ...

				await call.answer('🗑 Папка очищена' if v == len(files) else f'🗑 Удалено {v} из {len(files)}', show_alert=True)
				update_b()
			elif sub_menu in ['path_names', 'path_surnames', 'path_bio', 'path_chatlists', 'path_auto_join']:
				await aiofiles.open(f"{_data_dict[sub_menu]}", 'w', encoding='utf-8')
				await call.answer('🗑 Файл очищен', show_alert=True)
				update_b()


		elif q == 'edit':
			if sub_menu in ['bot_token', 'notify_user_id', 'admin_ids', 'proxy']:
				msg = await call.message.edit_text(f'<b>✏️ Введите новые данные для <i>{t.get(sub_menu, sub_menu)}</i></b>', reply_markup=kb_sup_menu('bback'))
				await state.set_state(states.change_smth)
				await state.update_data(sub_menu=sub_menu, msg=msg)

		elif q == 'get':
			if sub_menu in ['path_names', 'path_surnames', 'path_bio', 'path_chatlists', 'path_auto_join']:
				try:
					await call.message.answer_document(FSInputFile(_data_dict[sub_menu]), reply_markup=kb_delete())
					await call.answer()
				except: await call.answer('Файл пустой', show_alert=True)
			elif sub_menu in ['path_sessions_spamblock', 'path_sessions', 'path_avatars', 'path_channels_avatars']:
				folder_path = _data_dict[sub_menu]
				await send_files_as_zip(call, folder_path)
		else:
			await call.message.edit_text(f'<b>⚙️ Неизвестное меню</b>', reply_markup=kb_sup_menu())
	
	elif cd[1] == 'change_':
		sub_menu = cd[2]
		q = cd[-1] if len(cd) > 4 else cd[3]

		if q.split('$')[0] in ['Каналы', 'Чаты', 'Личные сообщения', 'avatar', 'name_surname', 'bio', 'self_channel', 'disable_notify', 'auto_join_ft', 'privacy_settings', 'previous_avatars', 'chatlists', 'invite_to', 'channels', 'stories', 'dm', 'generate_text', 'enable_likes', 'forward_enabled', 'notify', 'advanced_check', 'replace_session']:
			v = q.split('$')[0]
			z = json.loads((await (await aiofiles.open(f"config.json", 'r', encoding='utf-8')).read()))
			_data_dict[sub_menu][v] = not _data_dict[sub_menu][v]
			z[sub_menu][v] = _data_dict[sub_menu][v]

			async with aiofiles.open(f"config.json", 'w', encoding='utf-8') as f1:
				await f1.write(json.dumps(z, indent=4))

			try: await call.message.edit_text(f'<b>⚙️ Что изменить в <i>{t.get(sub_menu, sub_menu)}</i></b>', reply_markup=kb_cfg_menu(sub_menu))
			except Exception as e: await call.answer(f'Ошибка: {e}')

		elif q == 'edit':
			last_q = cd[3]
			if last_q in ['generate_text', 'openai_api_key', 'gpt_dialog_story', 'gpt_not_working_answer_variants', 'time_before_message', 'default_message', 'spam_channels', 'parse_chats', 'enable_likes', 'parse_invites', 'parse_chats', 'name_surname', 'bio', 'chatlists', 'disable_notify', 'auto_join_ft', 'privacy_settings', 'previous_avatars', 'title', 'about', 'enabled', 'path_to_folder', 'username', 'length', 'symbols', 'message', 'text', 'forward_from_username', 'forward_from_message_id']:
				msg = await call.message.edit_text(f'<b>✏️ Введите новые данные для <i>{t.get(last_q, last_q)}</i> в <i>{t.get(sub_menu, sub_menu)}</i></b>', reply_markup=kb_cfg_menu(sub_menu=sub_menu, q='bback'))
				await state.set_state(states.change_smth_)
				await state.update_data(sub_menu=sub_menu, q=last_q, msg=msg)

		elif q in ['generate_text', 'openai_api_key', 'gpt_dialog_story', 'gpt_not_working_answer_variants', 'time_before_message', 'default_message', 'spam_channels', 'parse_chats', 'enable_likes', 'parse_invites', 'parse_chats', 'name_surname', 'bio', 'chatlists', 'disable_notify', 'auto_join_ft', 'privacy_settings', 'previous_avatars', 'title', 'about', 'enabled', 'path_to_folder', 'username', 'length', 'symbols', 'message', 'text', 'forward_from_username', 'forward_from_message_id']:
			z = f'\nТекущее значение: <code>{_data_dict[sub_menu][q]}</code>'
			msg = await call.message.edit_text(f'<b>⚙️ Выберите действие для <i>{t.get(q, q)}</i> в <i>{t.get(sub_menu, sub_menu)}</i>{z}</b>', reply_markup=kb_cfg_menu(sub_menu=sub_menu, q=q))

		else:
			await call.message.edit_text(f'<b>⚙️ Неизвестное меню</b>', reply_markup=kb_cfg_menu())

	elif cd[1] == 'close':
		try: await call.message.delete()
		except: ...



# STATE - states.change_smth
@main_router.message(StateFilter(states.change_smth), F.text)
async def states_change_smth(message: Message, state: FSMContext):
	mt = message.text.strip()
	try: mt = ast.literal_eval(mt)
	except: ...
	state_data = await state.get_data()
	await delmsg(state_data['msg'], message)

	if state_data['sub_menu'] in ['path_names', 'path_surnames', 'path_bio', 'path_chatlists', 'path_auto_join']:
		z = (await (await aiofiles.open(f"{_data_dict[state_data['sub_menu']]}", 'r', encoding='utf-8')).readlines())
		e = '\n' if len(z) > 0 and z[-1] == '' else ''
		async with aiofiles.open(f"{_data_dict[state_data['sub_menu']]}", 'a', encoding='utf-8') as f1:
			await f1.write(f"{e}{mt}\n")

		await state.clear()
		await message.answer('<b>✅ Данные добавлены в файл</b>', reply_markup=kb_sup_menu(state_data['sub_menu']))
		update_b()

	elif state_data['sub_menu'] in ['bot_token', 'admin_ids', 'notify_user_id', 'proxy']:
		_data_dict[state_data['sub_menu']] = mt

		z = json.loads((await (await aiofiles.open(f"config.json", 'r', encoding='utf-8')).read()))
		z[state_data['sub_menu']] = mt

		async with aiofiles.open(f"config.json", 'w', encoding='utf-8') as f1:
			await f1.write(json.dumps(z, indent=4))

		await state.clear()
		await message.answer('<b>✅ Значение изменено</b>', reply_markup=kb_sup_menu(state_data['sub_menu']))
		update_b()



def extract_session_files(zip_path: str, save_path: str):
	v = 0
	with zipfile.ZipFile(zip_path, 'r') as zip_ref:
		for file in zip_ref.namelist():
			if file.endswith('.session'):
				extracted_path = zip_ref.extract(file, save_path)
				filename = os.path.basename(extracted_path)
				filename = f'{".".join(filename.split(".")[0:-1])}-{random.randint(100,999)}.{filename.split(".")[-1]}'
				final_path = os.path.join(save_path, filename)
				if extracted_path != final_path:
					os.rename(extracted_path, final_path)
				v += 1
	
	for root, dirs, files in os.walk(save_path, topdown=False):
		for name in dirs:
			shutil.rmtree(os.path.join(root, name))
	
	def renamed(dirpath, names):
		new_names = []
		for old in names:
			try: new = old.encode('cp437').decode('cp866')
			except UnicodeEncodeError: new = old
			new_names.append(new)
			try:
				os.rename(os.path.join(dirpath, old), os.path.join(dirpath, new))
			except Exception as e:
				print(f"Error renaming {old} to {new}: {e}")
		return new_names
	
	for dirpath, dirs, files in os.walk(save_path, topdown=True):
		renamed(dirpath, files)
		dirs[:] = renamed(dirpath, dirs)
	
	return v




@main_router.message(StateFilter(states.change_smth), F.document)
async def states_change_smth_document(message: Message, state: FSMContext):
	state_data = await state.get_data()
	await delmsg(state_data['msg'], message)

	if state_data['sub_menu'] in ['path_sessions']:
		document = message.document
		file_path = os.path.join(_data_dict[state_data['sub_menu']], f'{".".join(document.file_name.split(".")[0:-1])}-{random.randint(100,999)}.{document.file_name.split(".")[-1]}')

		if document.file_name.endswith('.session'):
			await bot.download(document, file_path)
			v = 1
			text = f'<b>✅ Добавлено сессий:</b>  <code>{v} шт.</code>'
		elif document.file_name.endswith('.zip'):
			zip_temp_path = file_path + ".zip"
			await bot.download(document, zip_temp_path)
			v = await asyncio.get_event_loop().run_in_executor(None, extract_session_files, zip_temp_path, _data_dict[state_data['sub_menu']])
			await aiofiles.os.remove(zip_temp_path)
			text = f'<b>✅ Добавлено сессий:</b>  <code>{v} шт.</code>'
		else:
			text = '⚠️ Данный формат файла не поддерживается.'
	
	await state.clear()
	await message.answer(text, reply_markup=kb_sup_menu(state_data['sub_menu']))
	update_b()

@main_router.message(StateFilter(states.change_smth), F.photo)
async def states_change_smth_document(message: Message, state: FSMContext):
	state_data = await state.get_data()
	await delmsg(state_data['msg'], message)

	if state_data['sub_menu'] in ['path_avatars', 'path_channels_avatars']:
		photo = message.photo[-1]
		file = await bot.download(photo, os.path.join(_data_dict[state_data['sub_menu']], f"{photo.file_unique_id}-{random.randint(100,999)}.jpg"))
	await state.clear()
	await message.answer('<b>Фото успешно добавлено</b>', reply_markup=kb_sup_menu(state_data['sub_menu']))
	update_b()





# STATE - states.change_smth_
@main_router.message(StateFilter(states.change_smth_), F.text)
async def states_change_smth_(message: Message, state: FSMContext):
	mt = message.text.strip()
	try: mt = ast.literal_eval(mt)
	except: ...

	state_data = await state.get_data()
	await delmsg(state_data['msg'], message)

	_data_dict[state_data['sub_menu']][state_data['q']] = mt

	z = json.loads((await (await aiofiles.open(f"config.json", 'r', encoding='utf-8')).read()))
	z[state_data['sub_menu']][state_data['q']] = mt

	async with aiofiles.open(f"config.json", 'w', encoding='utf-8') as f1:
		await f1.write(json.dumps(z, indent=4))

	await state.clear()
	z = f'\nТекущее значение: <code>{_data_dict[state_data["sub_menu"]][state_data["q"]]}</code>'
	await message.answer(f'<b>✅ Значение изменено{z}</b>', reply_markup=kb_cfg_menu(state_data['sub_menu'], state_data['q']))
	update_b()






@main_router.message(F.text)
async def handler_text(message: Message, state: FSMContext):
	if message.from_user.id not in _data_dict['admin_ids']: return
	mt = message.text
	await message.answer(f'<b>⚙️ Выберите что изменить</b>', reply_markup=kb_main_menu())


#################################################################################################################################
async def main(temp: dict = {}, update_func = lambda: ..., func_spam_block_check = lambda: 0) -> None:
	global _data_dict, update_b, spam_block_check
	_data_dict = temp
	update_b = update_func
	spam_block_check = func_spam_block_check
	dp = Dispatcher()
	dp.include_router(main_router)
	await dp.start_polling(bot)


if __name__ == '__main__':
	logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s', level=logging.ERROR, stream=sys.stdout)
	asyncio.run(main(json.loads(open('config.json', 'r', encoding='utf-8').read())))