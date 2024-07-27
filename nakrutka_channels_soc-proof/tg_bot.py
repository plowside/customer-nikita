import asyncio, logging, sqlite3, json, sys

from aiogram import Bot, Dispatcher, Router, F, html
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.filters import StateFilter
from aiogram.enums import ParseMode, ContentType
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import *


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

texts = {'channel':'🗑 Канал'}


main_router = Router()

class states(StatesGroup):
	change_service_id = State()
#################################################################################################################################
@main_router.callback_query(F.data.startswith('utils'), StateFilter('*'))
async def handler_utils(call: CallbackQuery, state: FSMContext):
	if call.from_user.id not in admin_ids: return
	await state.clear()
	cd = call.data.split(':')

	if cd[1] == 'change_service_id':
		boost_target = cd[2]
		await state.set_state(states.change_service_id)
		msg = await call.message.edit_text(f'<b>⚙️ Отправьте новый ID сервиса накрутки для <code>{texts[boost_target]}</code></b>', reply_markup=ikb_construct([ikb('❌ Отменить', data='utils:close')]))
		await state.update_data(boost_target=boost_target, msg=msg)

	elif cd[1] == 'close':
		try: await call.message.delete()
		except: ...

@main_router.message(StateFilter(states.change_service_id), F.text)
async def states_change_service_id(message: Message, state: FSMContext):
	if message.from_user.id not in admin_ids: return
	mt = message.text
	state_data = await state.get_data()
	boost_target = state_data['boost_target']

	for x in [state_data['msg'], message]:
		try: await x.delete()
		except: ...
	try: new_service_id = int(mt)
	except:
		msg = await message.answer(f'<b>⚙️ Отправьте новый ID сервиса накрутки для <code>{texts[boost_target]}</code> ЧИСЛОМ И БЕЗ ПОСТОРОННИХ СИМВОЛОВ</b>', reply_markup=ikb_construct([ikb('❌ Отменить', data='utils:close')]))
		await state.update_data(msg=msg)
		return

	with open('config.py', 'r', encoding='utf-8') as file:
		config_content = file.read()
	start_index = config_content.find('soc_proof_services = {')
	end_index = config_content.find('}#', start_index) + 1
	soc_proof_services_str = config_content[start_index:end_index]
	soc_proof_services = eval(soc_proof_services_str[soc_proof_services_str.find('=') + 1:].strip())
	soc_proof_services[boost_target]['service_id'] = new_service_id
	new_config_content = config_content[:start_index] + f'soc_proof_services = {str(soc_proof_services)}' + config_content[end_index:]
	with open('config.py', 'w', encoding='utf-8') as file:
		file.write(new_config_content)

	_soc_proof_services[boost_target]['service_id'] = new_service_id
	await message.answer(f'<b>✅ Новый ID сервиса накрутки для <code>{texts[boost_target]}</code>:  <code>{new_service_id}</code></b>', reply_markup=ikb_construct([ikb('❌ Закрыть', data='utils:close')]))
	await state.clear()

@main_router.message(F.text)
async def handler_text(message: Message, state: FSMContext):
	if message.from_user.id not in admin_ids: return
	mt = message.text
	await message.answer(f'<b>⚙️ Выберите объект накрутки</b>', reply_markup=ikb_construct([ikb('🗑 Канал', data='utils:change_service_id:channel')]))


#################################################################################################################################
async def main(temp) -> None:
	global _soc_proof_services
	_soc_proof_services = temp
	bot = Bot(token=bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
	dp = Dispatcher()
	dp.include_router(main_router)
	await dp.start_polling(bot)


if __name__ == "__main__":
	logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s', level=logging.ERROR, stream=sys.stdout)
	asyncio.run(main())