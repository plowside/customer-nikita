import aiofiles.os, aiofiles, asyncio, logging, sqlite3, zipfile, shutil, random, json, sys, ast, os

from aiogram import Bot, Dispatcher, Router, F, html
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton, KeyboardButton, FSInputFile
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.filters import StateFilter
from aiogram.enums import ParseMode, ContentType
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from telethon import types

from config import *

report_reasons_types = {
	'spam':					types.InputReportReasonSpam,
	'violence':				types.InputReportReasonViolence,
	'child_abuse':			types.InputReportReasonChildAbuse,
	'pornography':			types.InputReportReasonPornography,
	'copyright права':		types.InputReportReasonCopyright,
	'illegal_drugs':		types.InputReportReasonIllegalDrugs,
	'personal_details':		types.InputReportReasonPersonalDetails,
	'other':				types.InputReportReasonOther,
	'fake':					types.InputReportReasonFake,
	'geo_irrelevan':		types.InputReportReasonGeoIrrelevant
}
report_objs_types = {
	'user':		types.InputPeerUser,
	'bot':		types.InputPeerUser,
	'channel':	types.InputPeerChannel,
	'message':	types.InputPeerChannelFromMessage,
	'avatar':	'🖼 Аватарка',
	'story':	'🏞 История',
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
		[ikb('🚀 Отправить репорт', data='utils:menu:report')]
	)

def kb_report_menu(state: str, target_reason: str = None):
	if state == 'target':
		return ikb_construct(
			*[[ikb(report_objs[x], data=f'utils:report:{x}') for x in list(report_objs.keys())[i:i+2]] for i in range(0, len(report_objs), 2)],
			back_button=ikb('↪ Назад', data=f'utils:menu:main')
		)
	elif state == 'target_creds':
		return ikb_construct(
			back_button=ikb('↪ Назад', data=f'utils:menu:report')
		)
	elif state == 'target_reason':
		#report_reasons = report_reasons
		return ikb_construct(
			*[[ikb(report_reasons[x], data=x) for x in list(report_reasons.keys())[i:i+2]] for i in range(0, len(report_reasons), 2)],
			back_button=ikb('↪ Назад', data=f'utils:menu:report')
		)
	elif state == 'target_message':
		return ikb_construct(
			*[[ikb(profiles.get(target_reason, {}).get(x, {}).get('name', f'Профиль {i}'), data=f'profile:{x}') for x in list(profiles.get(target_reason, {}).keys())[i:i+2]] for i in range(0, len(profiles.get(target_reason, {})), 2)],
			[ikb('⏭ Пропустисть', data='skip')],
			back_button=ikb('↪ Назад', data=f'utils:menu:report')
		)
	elif state == 'target_amount':
		return ikb_construct(
			back_button=ikb('↪ Назад', data=f'utils:menu:report')
		)
	elif state == 'complete':
		return ikb_construct(
			[ikb('🚀 Запустить задачу', data=f'run')],
			back_button=ikb('↪ Назад', data=f'utils:menu:report')
		)
	else:
		return ikb_construct(
			back_button=ikb('↪ Назад', data=f'utils:menu:main')
		)


main_router = Router()
bot = Bot(token=bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

class states(StatesGroup):
	report = State()


async def delmsg(*msgs):
	for x in msgs:
		try: await x.delete()
		except: ...
#################################################################################################################################
@main_router.callback_query(F.data.startswith('utils'), StateFilter('*'))
async def handler_utils(call: CallbackQuery, state: FSMContext):
	if call.from_user.id not in admin_ids: return
	await state.clear()
	cd = call.data.split(':')

	if cd[1] == 'menu':
		menu = cd[2]
		if menu == 'main':
			await call.message.edit_text(f'<b>⚙️ Выберите что изменить</b>', reply_markup=kb_main_menu())
		elif menu == 'report':
			await call.message.edit_text(f'<b>🚀 Отправка репорта</b>\n\n<i>Выберите объект репорта</i>', reply_markup=kb_report_menu(state='target'))
		else:
			await call.answer('Неизвестное меню')

	elif cd[1] == 'report':
		target_obj = cd[2]

		if len(cd) == 3:
			this_state = 'target_creds'
			msg = await call.message.edit_text(f'<b>🚀 Отправка репорта</b>\n└ Объект: <b>{report_objs[target_obj]}</b>\n<i>Введите данные объекта репорта (username)</i>', reply_markup=kb_report_menu(state=this_state))
			await state.set_state(states.report)
			await state.update_data(state=this_state, target_obj=target_obj, msgs=[msg])


	elif cd[1] == 'close':
		try: await call.message.delete()
		except: ...





@main_router.message(StateFilter(states.report))
async def states_router(message: Message, state: FSMContext):
	mt = message.text
	state_data = await state.get_data()

	if state_data['state'] == 'target_creds':
		try:
			target_creds = int(mt.strip())
			msg = await message.answer('<b>Введите юзернейм, id не принимается</b>')
			await state.update_data(msgs=[*state_data["msgs"], message, msg])
			return
		except:
			target_creds = mt.strip().replace('@', '').split('/')[-1]
		this_state = 'target_reason'
		msg = await message.answer(f'<b>🚀 Отправка репорта</b>\n├ Объект: <b>{report_objs[state_data["target_obj"]]}</b>\n└ Данные:  <code>{target_creds}</code>\n<i>Выберите причину репорта</i>', reply_markup=kb_report_menu(state=this_state))
		await delmsg(*state_data['msgs'], message)
		await state.update_data(target_creds=target_creds, state=this_state, msgs=[msg])
	
	elif state_data['state'] == 'target_reason':
		msg = await message.answer('Выберите кнопку')
		await state.update_data(msgs=[*state_data["msgs"], message, msg])

	elif state_data['state'] == 'target_message':
		try: target_message = ast.literal_eval(mt)
		except: target_message = mt
		if isinstance(target_message, list) and not all(isinstance(item, (str, int, float)) for item in target_message):
			msg = await message.answer('❌ Введенные данные не подходят под формат <code>[str]</code>.')
			await state.update_data(msgs=[*state_data["msgs"], message, msg])
			return
		this_state = 'target_amount'
		available_sessions = len(sesmanage_client.clients["offline"]) + len(sesmanage_client.clients["online"])
		msg = await message.answer(f'<b>🚀 Отправка репорта</b>\n├ Объект: <b>{report_objs[state_data["target_obj"]]}</b>\n├ Данные:  <code>{state_data["target_creds"]}</code>\n├ Причина:  <code>{report_reasons[state_data["target_reason"]]}</code>\n└ Сообщение:  <code>{target_message if target_message else "Нет"}</code>\n<i>Введите количество сессий для репорта\nДоступно:  <code>{available_sessions} шт.</code></i>', reply_markup=kb_report_menu(state=this_state))
		await delmsg(*state_data["msgs"], message)
		await state.update_data(target_message=target_message, state=this_state, msgs=[msg])
	
	elif state_data['state'] == 'target_amount':
		try: target_amount = int(mt)
		except:
			msg = await message.answer('Введите число без посторонних символов')
			await state.update_data(msgs=[*state_data["msgs"], message, msg])
			return

		this_state = 'complete'
		msg = await message.answer(f'<b>🚀 Отправка репорта</b>\n├ Объект: <b>{report_objs[state_data["target_obj"]]}</b>\n├ Данные:  <code>{state_data["target_creds"]}</code>\n├ Причина:  <code>{report_reasons[state_data["target_reason"]]}</code>\n├ Сообщение:  <code>{state_data["target_message"] if state_data["target_message"] else "Нет"}</code>\n└ Количество сессий:  <code>{target_amount} шт.</code>\n<i>⚠️ Вы уверены что хотите запустить отправку репортов?</i>', reply_markup=kb_report_menu(state=this_state))
		await delmsg(*state_data["msgs"], message)
		await state.update_data(target_amount=target_amount, state=this_state, msgs=[msg])


@main_router.callback_query(StateFilter(states.report))
async def states_router_(call: CallbackQuery, state: FSMContext):
	cd = call.data.split(':')
	state_data = await state.get_data()

	if state_data['state'] == 'target_reason':
		target_reason = cd[0]
		this_state = 'target_message'
		msg = await call.message.edit_text(f'<b>🚀 Отправка репорта</b>\n├ Объект: <b>{report_objs[state_data["target_obj"]]}</b>\n├ Данные:  <code>{state_data["target_creds"]}</code>\n└ Причина:  <code>{report_reasons[target_reason]}</code>\n<i>Введите сообщение (комментарий, пояснение) для репорта</i>', reply_markup=kb_report_menu(state=this_state, target_reason=target_reason))
		await state.update_data(target_reason=target_reason, state=this_state)

	elif state_data['state'] == 'target_message':
		if cd[0] == 'skip':
			target_message = None
		elif cd[0] == 'profile':
			target_message = profiles.get(state_data["target_reason"], {}).get(cd[1], {}).get('values', None)
		this_state = 'target_amount'
		available_sessions = len(sesmanage_client.clients["offline"]) + len(sesmanage_client.clients["online"])
		msg = await call.message.edit_text(f'<b>🚀 Отправка репорта</b>\n├ Объект: <b>{report_objs[state_data["target_obj"]]}</b>\n├ Данные:  <code>{state_data["target_creds"]}</code>\n├ Причина:  <code>{report_reasons[state_data["target_reason"]]}</code>\n└ Сообщение:  <code>{target_message if target_message else "Нет"}</code>\n<i>Введите количество сессий для репорта\nДоступно:  <code>{available_sessions} шт.</code></i>', reply_markup=kb_report_menu(state=this_state))
		await state.update_data(target_message=target_message, state=this_state)
	
	elif state_data['state'] == 'target_amount':
		target_amount = cd[0]
		this_state = 'complete'
		msg = await call.message.edit_text(f'<b>🚀 Отправка репорта</b>\n├ Объект: <b>{report_objs[state_data["target_obj"]]}</b>\n├ Данные:  <code>{state_data["target_creds"]}</code>\n├ Причина:  <code>{report_reasons[state_data["target_reason"]]}</code>\n├ Сообщение:  <code>{state_data["target_message"] if state_data["target_message"] else "Нет"}</code>\n└ Количество сессий:  <code>{target_amount} шт.</code>\n<i>⚠️ Вы уверены что хотите запустить отправку репортов?</i>', reply_markup=kb_report_menu(state=this_state))
		await state.update_data(target_amount=target_amount, state=this_state)

	elif state_data['state'] == 'complete':
		this_state = 'completed'
		msg = await call.message.answer(f'<b>🚀 Отправка репорта</b>\n├ Объект: <b>{report_objs[state_data["target_obj"]]}</b>\n├ Данные:  <code>{state_data["target_creds"]}</code>\n├ Причина:  <code>{report_reasons[state_data["target_reason"]]}</code>\n├ Сообщение:  <code>{state_data["target_message"] if state_data["target_message"] else "Нет"}</code>\n└ Количество сессий:  <code>{state_data["target_amount"]} шт.</code>\n\n<i>✅ Задача запущена</i>', reply_markup=kb_report_menu(state=this_state))
		await state.clear()
		await delmsg(*state_data["msgs"])

		if state_data['target_obj'] in ['user', 'bot', 'channel']:
			if isinstance(state_data['target_creds'], str):
				user = await sesmanage_client.get_user_id(state_data['target_creds'])
				print('user', user, type(user))
				if not user:
					await msg.reply(f'<b>🚀 Отправка репорта</b>\n\n<i>❌ Не удалось найти пользователя с таким username: @{state_data["target_creds"]}</i>', reply_markup=kb_delete())
					return

			peer_type = report_objs_types[state_data['target_obj']]

		asyncio.get_event_loop().create_task(sesmanage_client.start_report(sender_id=call.from_user.id, amount=state_data['target_amount'], username=state_data['target_creds'], peer=peer_type, reason=report_reasons_types[state_data['target_reason']](), message=state_data['target_message']))



@main_router.message(F.text)
async def handler_text(message: Message, state: FSMContext):
	if message.from_user.id not in admin_ids: return
	mt = message.text
	await message.answer(f'<b>⚙️ Выберите что изменить</b>', reply_markup=kb_main_menu())


#################################################################################################################################
async def main(temp) -> None:
	global sesmanage_client
	sesmanage_client = temp

	dp = Dispatcher()
	dp.include_router(main_router)
	logging.info('Бот запущен')
	await dp.start_polling(bot)


if __name__ == '__main__':
	logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s', level=logging.ERROR, stream=sys.stdout)
	asyncio.run(main(''))