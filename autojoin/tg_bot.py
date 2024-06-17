import asyncio, logging, sqlite3, time, json, sys

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
def DB_DictFactory(cursor, row):
	_ = {}
	for i, column in enumerate(cursor.description):
		_[column[0]] = row[i]
	return _

con = sqlite3.connect('db.db', check_same_thread=False)
con.row_factory = DB_DictFactory
cur = con.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS sessions(
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	tg_id INTEGER,
	session_name TEXT,
	unix INTEGER
)''')
cur.execute('''CREATE TABLE IF NOT EXISTS tasks(
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	task_type TEXT,
	task_data TEXT,
	task_status TEXT,
	unix INTEGER
)''')
#################################################################################################################################
main_router = Router()

class states(StatesGroup):
	answer_msg = State()


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

def get_unix():
	return int(time.time())
#################################################################################################################################
@main_router.callback_query(F.data.startswith('utils'), StateFilter('*'))
async def handler_utils(call: CallbackQuery, state: FSMContext):
	cd = call.data.split(':')

	if cd[1] == 'answer':
		await call.answer()
		await state.set_state(states.answer_msg)
		m = await call.message.reply(f"<b>Отправьте ответ на сообщение</b>\n<i>Метод ответа:</i>  <code>Ответ с указаннием оригинального сообщения</code>", reply_markup=ikb_construct([ikb('Статус: ↪️ Ответ', data='change_rotation')], [ikb('❌ Отмена', data='utils:close')]))
		#m = await call.message.reply(f"<b>Отправьте ответ на сообщение</b>\n<i>Метод ответа:</i>  <code>{'Обычное сообщение' if data['answer_method'] == 'answer' else 'Ответ с указаннием оригинального сообщения'}</code>", reply_markup=ikb_construct(InlineKeyboardMarkup(row_width=1), {'Статус: ↪️ Ответ': 'cd^change_rotation', '❌ Отмена': 'cd^utils:close'}))
		await state.update_data(from_user_id=int(cd[2]), to_user_id=int(cd[3]), message_id=int(cd[4]), answer_method='reply', m=m)

	elif cd[1] == 'close':
		try: await call.message.delete()
		except: ...

@main_router.message(StateFilter(states.answer_msg))
async def states_answer_msg(message: Message, state: FSMContext):
	mt = message.text
	state_data = await state.get_data()
	
	for x in [state_data['m'], message]:
		try: await x.delete()
		except: ...

	cur.execute('INSERT INTO tasks(task_type, task_data, task_status, unix) VALUES (?, ?, ?, ?)', ['send_message', json.dumps({'from_user_id': state_data['from_user_id'], 'to_user_id': state_data['to_user_id'], 'message_id': state_data['message_id'], 'message_text': mt, 'answer_method': state_data['answer_method']}), 'created', get_unix()])
	con.commit()
	await message.answer('<b>Задача для ответа на сообщение создана!</b>', reply_markup=ikb_construct([ikb('❌ Отмена', data='utils:close')]))
	await state.clear()

@main_router.callback_query(StateFilter(states.answer_msg))
async def handler_utils(call: CallbackQuery, state: FSMContext):
	cd = call.data.split(':')

	if cd[0] == 'change_rotation':
		state_data = await state.get_data()

		if state_data['answer_method'] == 'reply':
			answer_method = 'answer'
		else:
			answer_method = 'reply'
		await state.update_data(answer_method=answer_method)
		try: await call.message.edit_text(f"<b>Отправьте ответ на сообщение</b>\n<i>Метод ответа:</i>  <code>{'Обычное сообщение' if answer_method == 'answer' else 'Ответ с указаннием оригинального сообщения'}</code>", reply_markup=ikb_construct([ikb('Статус: '+ ('↪️ Ответ' if answer_method == 'reply' else '⬅️ Сообщение'), data='change_rotation')], [ikb('❌ Отмена', data='utils:close')]))
		except: ...


@main_router.message(F.text)
async def handler_text(message: Message, state: FSMContext):
	mt = message.text
	await message.answer_sticker(sticker='CAACAgIAAxkBAAJKKmYzQluqmMsLYtuc9kkbwd317Y8zAAI3DAACIdExSUDPHRXfCywVNAQ')
#################################################################################################################################
async def main() -> None:
	bot = Bot(token=bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
	dp = Dispatcher()
	dp.include_router(main_router)
	await dp.start_polling(bot)


if __name__ == "__main__":
	logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s', level=logging.INFO, stream=sys.stdout)
	asyncio.run(main())