import asyncio, logging, sqlite3, sys

from aiogram import Bot, Dispatcher, Router, F, html
from aiogram.types import CallbackQuery, Message
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
	uid INTEGER,
	session_name TEXT
)''')
cur.execute('''CREATE TABLE IF NOT EXISTS tasks(
	message_id INTEGER,
	url TEXT,
	command TEXT,
	status BOOL DEFAULT False
)''')
#################################################################################################################################
main_router = Router()

class states(StatesGroup):
	answer_msg = State()


#################################################################################################################################
@main_router.message(F.text)
async def handler_text(message: Message, state: FSMContext):
	mt = message.text
	await message.answer_sticker(sticker='CAACAgIAAxkBAAJKKmYzQluqmMsLYtuc9kkbwd317Y8zAAI3DAACIdExSUDPHRXfCywVNAQ')


@main_router.callback_query(F.data.startswith('utils'), StateFilter('*'))
async def handler_utils(call: CallbackQuery, state: FSMContext):
	cd = call.data.split(':')

	if cd[1] == 'answer':
		await call.answer()
		await state.set_state(states.answer_msg)
		m = await call.message.reply(f"<b>Отправьте ответ на сообщение</b>\n<i>Метод ответа:</i>  <code>{'Обычное сообщение' if data['answer_method'] == 'answer' else 'Ответ с указаннием оригинального сообщения'}</code>", reply_markup=kb_construct(InlineKeyboardMarkup(row_width=1), {'Статус: ↪️ Ответ': 'cd^change_rotation', '❌ Отмена': 'cd^utils:close'}))
		await state.update_data(from_id=cd[2], to_id=cd[3], m_id=cd[4], answer_method='reply', m=m)

	elif cd[1] == 'close':
		try: await call.message.delete()
		except: ...

@main_router.message(states.answer_msg, F.any)
async def states_answer_msg(message: Message, state: FSMContext):
	mt = message.text
	state_data = await state.get_data()
	
	for x in [state_data['m'], message]:
		try: await x.delete()
		except: ...
	cur.execute('INSERT INTO tasks VALUES (?, ?, ?, ?)', [f"{state_data['from_id']}:{state_data['to_id']}:{state_data['m_id']}:{state_data['answer_method']}", mt, 'send_msg', False])
	con.commit()
	await message.answer('<b>Задача для ответа на сообщение создана!</b>', reply_markup=kb_construct(InlineKeyboardMarkup(), {'❌ Закрыть': 'cd^utils:close'}))
	await state.clear()

@main_router.callback_query(states.answer_msg)
async def handler_utils(call: CallbackQuery, state: FSMContext):
	cd = call.data.split(':')

	if cd[0] == 'change_rotation':
		state_data = await state.get_data()

		if state_data['answer_method'] == 'reply':
			state_data['answer_method'] = 'answer'
		else:
			state_data['answer_method'] = 'reply'
		try: await call.message.edit_text(f"<b>Отправьте ответ на сообщение</b>\n<i>Метод ответа:</i>  <code>{'Обычное сообщение' if state_data['answer_method'] == 'answer' else 'Ответ с указаннием оригинального сообщения'}</code>", reply_markup=kb_construct(InlineKeyboardMarkup(row_width=1), {'Статус: '+ ('↪️ Ответ' if state_data['answer_method'] == 'reply' else '⬅️ Сообщение'): 'cd^change_rotation', '❌ Отмена': 'cd^utils:close'}))
		except: ...



#################################################################################################################################
async def main() -> None:
	bot = Bot(token=bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
	dp = Dispatcher()
	dp.include_router(main_router)
	await dp.start_polling(bot)


if __name__ == "__main__":
	logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s', level=logging.INFO, stream=sys.stdout)
	asyncio.run(main())