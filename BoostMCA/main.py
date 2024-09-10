# -*- coding: utf-8 -*-
import asyncio, aiogram, threading, logging, random, string, math, json, time, traceback, re, os, uuid

from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.dispatcher.filters import BoundFilter
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import ChatActions
from aiogram import Bot, types

from aiogram.utils.exceptions import (Unauthorized, InvalidQueryID, TelegramAPIError, UserDeactivated,
									CantDemoteChatCreator, MessageNotModified, MessageToDeleteNotFound,
									MessageTextIsEmpty, RetryAfter, CantParseEntities, MessageCantBeDeleted,
									TerminatedByOtherGetUpdates, BotBlocked)

from datetime import datetime, timedelta, timezone


from middleware import ThrottlingMiddleware
from functions import *
from keyboards import *
from config import *
from loader import *



#################################################################################################################################
logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s', level=logging.INFO,)
#logging.getLogger("aiogram").setLevel(logging.INFO)
#logging.getLogger("asyncio").setLevel(logging.INFO)
#################################################################################################################################
class is_reg(BoundFilter):
	def __init__(self, is_self = False):
		self.is_self = is_self # Recurse bypass

	async def check(self, message: types.Message):
		uid, username, first_name = get_user(message)

		channels_to_join = [x for x in channels_data if not await check_channel(x, uid)]
		if len(channels_to_join) > 0:
			if not self.is_self: 
				if type(message) == aiogram.types.message.Message: await message.answer('<b>💬 Добро пожаловать!</b>\n\n<b>⚡️ Чтобы получить доступ, необходимо подписаться на канал.</b>', reply_markup=await kb_channels(uid, channels_to_join))
				else: await message.message.answer('<b>💬 Добро пожаловать!</b>\n\n<b>⚡️ Чтобы получить доступ, необходимо подписаться на канал.</b>', reply_markup=await kb_channels(uid, channels_to_join))
			return False

		async with db.pool.acquire() as conn:
			user_db = await conn.fetchrow('SELECT username, first_name, is_banned FROM users WHERE uid = $1', uid)
			if user_db:
				if user_db["username"] != username: await conn.execute('UPDATE users SET username = $1 WHERE uid = $2', username, uid)
				elif user_db['first_name'] != first_name: await conn.execute('UPDATE users SET first_name = $1 WHERE uid = $2', first_name, uid)
				

				if user_db['is_banned']: return False
			else:
				if not self.is_self: return False

				referral_from_id = message.get_args() if message.get_args() not in ('', 'none', 'None') else None
				try:
					if not referral_from_id: await conn.execute('INSERT INTO users (uid, username, first_name, registration_date) VALUES ($1, $2, $3, $4)', uid, username, first_name, int(time.time()))
					else:
						await conn.execute('INSERT INTO users (uid, username, first_name, registration_date, referral_from_id) VALUES ($1, $2, $3, $4, $5)', uid, username, first_name, int(time.time()), referral_from_id)
				except: await conn.execute('INSERT INTO users (uid, username, first_name, registration_date) VALUES ($1, $2, $3, $4)', uid, username, first_name, int(time.time()))
				await admin_spam(f'<b>🔔 Новый пользователь!\n\n👤 Username: {format_user_url(uid, username, first_name)}\n🆔 Telegram ID: <code>{uid}</code></b>')
		return True
#################################################################################################################################

# Стартовая команда - /start
@dp.message_handler(is_reg(True), CommandStart(), state='*')
async def CommandStart_(message: types.Message, state: FSMContext):
	await state.finish()

	uid, username, first_name = get_user(message)
	await message.answer_photo(photo=open(images['start_msg'], 'rb'), caption=f'<b>💬 Добро пожаловать!</b>\n\n<b>🤖 Бусты МЦА</b> — бот, позволяющий тебе купить бусты (голоса) в канал для того чтобы поставить обои/реакции/истории и др. Лучшее качество и скорость во всем телеграме.\n \n<b>Отзывы - @boostmca</b>', reply_markup=await kb_menu(uid))


@dp.message_handler(is_reg(), content_types=['text'])
async def handler_text(message: types.Message, state: FSMContext, custom_data = None):
	mt = custom_data if custom_data else message.text
	ts = int(time.time())

	uid, username, first_name = get_user(message)
	user_db = await db.fetchrow('SELECT * FROM users WHERE uid = $1', uid)


	if mt == '💰 Профиль|Баланс':
		await message.answer_photo(photo=open(images['user_menu'], 'rb'), caption=f'<b>📱 Ваш профиль:</b>\n<i>Основная информация</i>\n\n🔑 ID:  <code>{uid}</code>\n🕜 Регистрация:  <code>{datetime.strftime(datetime.fromtimestamp(user_db["registration_date"]),"%d.%m.%Y")}</code>\n\n💳 Баланс:  <code>{round(user_db["balance"], 3)} ₽</code>', reply_markup=await kb_profile(user_db))

	elif mt == '❓ Ответы на вопросы':
		await message.answer_photo(photo=open(images['main_menu'], 'rb'), caption=f'<b>❓ {faq_text_ids[0]}</b>\n\n{faq_text[faq_text_ids[0]]}', reply_markup=await kb_faq())

	elif mt == 'ℹ️ Информация':
		await message.answer_photo(photo=open(images['main_menu'], 'rb'), caption=f'<b>ℹ️ Информация</b>\nОсновная информация и ссылки\n\n🕓 Дата запуска:  <code>{datetime.strftime(datetime.fromtimestamp(project_start_ts),"%d.%m.%Y")} ({math.ceil((ts - project_start_ts)/86400)} {morpher(math.ceil((ts - project_start_ts)/86400), "дней")})</code>\n👨‍💻 Администратор: <b>{username_support}</b>', reply_markup=await kb_about())

	elif mt == '🧑🏻‍💻 Админ меню':
		if uid in admin_ids: await message.answer('<b>🧑🏻‍💻 Админ меню</b>', reply_markup=await kb_admin_menu())

	elif mt == 'getdb':
		if uid in admin_ids: await message.answer_document(open('db.db','rb'))

	elif mt == '⭐️ Заказать бусты':
		return await smm_start_message(message, state)


@dp.errors_handler()
async def errors_handler(update, exception):
	# Не удалось изменить сообщение
	if isinstance(exception, MessageNotModified):
		# logging.exception(f"MessageNotModified: {exception}\nUpdate: {update}")
		return True

	# Пользователь заблокировал бота
	if isinstance(exception, BotBlocked):
		# logging.exception(f"BotBlocked: {exception}\nUpdate: {update}")
		return True

	if isinstance(exception, CantDemoteChatCreator):
		logging.exception(f"CantDemoteChatCreator: {exception}\nUpdate: {update}")
		return True

	# Не удалось удалить сообщение
	if isinstance(exception, MessageCantBeDeleted):
		#logging.exception(f"MessageCantBeDeleted: {exception}\nUpdate: {update}")
		return True

	# Сообщение для удаления не было найдено
	if isinstance(exception, MessageToDeleteNotFound):
		# logging.exception(f"MessageToDeleteNotFound: {exception}\nUpdate: {update}")
		return True

	# Сообщение пустое
	if isinstance(exception, MessageTextIsEmpty):
		# logging.exception(f"MessageTextIsEmpty: {exception}\nUpdate: {update}")
		return True

	# Пользователь удалён
	if isinstance(exception, UserDeactivated):
		# logging.exception(f"UserDeactivated: {exception}\nUpdate: {update}")
		return True

	# Бот не авторизован
	if isinstance(exception, Unauthorized):
		logging.exception(f"Unauthorized: {exception}\nUpdate: {update}")
		return True

	# Неверный Query ID
	if isinstance(exception, InvalidQueryID):
		# logging.exception(f"InvalidQueryID: {exception}\nUpdate: {update}")
		return True

	# Повторите попытку позже
	if isinstance(exception, RetryAfter):
		# logging.exception(f"RetryAfter: {exception}\nUpdate: {update}")
		return True

	# Уже имеется запущенный бот
	if isinstance(exception, TerminatedByOtherGetUpdates):
		print("You already have an active bot. Turn it off.")
		logging.exception(f"TerminatedByOtherGetUpdates: {exception}\nUpdate: {update}")
		return True

	# Ошибка в HTML/MARKDOWN разметке
	if isinstance(exception, CantParseEntities):
		logging.exception(f"CantParseEntities: {exception}\nUpdate: {update}")
		return True

	# Ошибка телеграм АПИ
	if isinstance(exception, TelegramAPIError):
		logging.exception(f"TelegramAPIError: {exception}\nUpdate: {update}")
		return True

	# Все прочие ошибки
	logging.exception(f"Exception: {exception}\nUpdate: {update}")

	try:
		try: os.makedirs('temp')
		except: pass
		f_name= f'temp/{time.time()}.txt'
		open(f_name, 'w', encoding='utf-8').write(f"{str(update)}\n\n{str(traceback.format_exc())}")
		for x in admin_ids:
			try: await bot.send_document(x, document=open(f_name, 'rb'), caption=f"<b>Exception:</b> <code>{exception}</code>", reply_markup=await kb_close())
			except: pass
		threading.Thread(target=os_delete, args=[f_name]).start()
	except: pass

	return True



##################################!!! HANDLERS - UTILS | TEMP - HANDLERS !!!############################################################
@dp.callback_query_handler(text_startswith='utils', state='*')
async def handler_utils(call: types.CallbackQuery, state: FSMContext, custom_data = None):
	cd = custom_data.split(':') if custom_data else call.data.split(':')

	if cd[1] == 'delete':
		try: await call.message.delete()
		except: pass
	
	elif cd[1] == 'faq':
		cur_faq_id = int(cd[3])
		
		try: await call.message.edit_media(media=types.InputMediaPhoto(media=open(images['main_menu'], 'rb'), caption=f'❓ <b>{faq_text_ids[cur_faq_id]}</b>\n\n{faq_text[faq_text_ids[cur_faq_id]]}'), reply_markup=await kb_faq(cur_faq_id))
		except: pass

	elif cd[1] == 'dm_user':
		target_uid = int(cd[2])
		text = users_messages.get(cd[3])
		if not text: return
		try: await bot.send_message(target_uid, text, reply_markup=await kb_close())
		except: pass

		await call.answer()

	elif cd[1] == 'check_sub':
		uid, username, first_name = get_user(call)
		for x in channels_data:
			await cache.delete(f"check_channel:{x}:{uid}")
		channels_to_join = [x for x in channels_data if not await check_channel(x, uid)]
		await delmsg(call.message)
		if len(channels_to_join) > 0:
			await call.message.answer('<b>⚠️ Подписка не найдена!</b>\n\n<b>⚡️ Чтобы получить доступ, необходимо подписаться на канал.</b>', reply_markup=await kb_channels(uid, channels_to_join))
		else:
			await call.message.answer_photo(photo=open(images['start_msg'], 'rb'), caption=f'<b>💬 Добро пожаловать!</b>\n\n<b>🤖 Бусты МЦА</b> — бот, позволяющий тебе купить бусты (голоса) в канал для того чтобы поставить обои/реакции/истории и др. Лучшее качество и скорость во всем телеграме.\n \n<b>Отзывы - @boostmca</b>', reply_markup=await kb_menu(uid))



@dp.callback_query_handler(text_startswith='temp')
async def handler_temp(call: types.CallbackQuery, state: FSMContext, custom_data = None):
	await state.finish()
	uid, username, first_name = get_user(call)

	cd = custom_data.split(':') if custom_data else call.data.split(':')

	if cd[1] == 'fastbalance': return await states_user_refill_balance(call.message, state, cd[2])
	
	elif cd[1] == 'finduser':
		try: await call.message.delete()
		except: pass
		return await states_admin_search_user(call.message, state, cd[2])


##################################!!! HANDLERS - USER - HANDLERS !!!#############################################################
class states_user(StatesGroup):
	refill_balance = State()
	activate_code = State()
	ref_balance_withdraw = State()


@dp.callback_query_handler(is_reg(), text_startswith='user')
async def handler_user(call: types.CallbackQuery, state: FSMContext, custom_data = None):
	await state.finish()
	cd = custom_data.split(':') if custom_data else call.data.split(':')
	ts = int(time.time())
	uid, username, first_name = get_user(call)
	
	if cd[1] == 'menu': 
		user_db = await db.fetchrow('SELECT * FROM users WHERE uid = $1', uid)

		try: await call.message.edit_media(media=types.InputMediaPhoto(media=open(images['user_menu'], 'rb'), caption=f'<b>📱 Ваш профиль:</b>\n<i>Основная информация</i>\n\n🔑 ID:  <code>{uid}</code>\n🕜 Регистрация:  <code>{datetime.strftime(datetime.fromtimestamp(user_db["registration_date"]),"%d.%m.%Y")}</code>\n\n💳 Баланс:  <code>{round(user_db["balance"], 3)} ₽</code>'), reply_markup=await kb_profile(user_db))
		except:
			await delmsg(call.message)
			await call.message.answer_photo(photo=open(images['user_menu'], 'rb'), caption=f'<b>📱 Ваш профиль:</b>\n<i>Основная информация</i>\n\n🔑 ID:  <code>{uid}</code>\n🕜 Регистрация:  <code>{datetime.strftime(datetime.fromtimestamp(user_db["registration_date"]),"%d.%m.%Y")}</code>\n\n💳 Баланс:  <code>{round(user_db["balance"], 3)} ₽</code>', reply_markup=await kb_profile(user_db))

	elif cd[1] == 'show_orders':
		orders = await db.fetch('SELECT * FROM orders WHERE uid = $1 ORDER BY id DESC', uid)
		if len(orders) == 0: return await call.answer('❗️ Вы ещё не создали ни один заказ!', show_alert=True)

		try: await call.message.edit_media(media=types.InputMediaPhoto(media=open(images['user_menu'], 'rb'), caption='<b>Ваши заказы</b>'), reply_markup=await kb_user_orders(orders))
		except:
			await delmsg(call.message)
			await call.message.answer_photo(photo=open(images['user_menu'], 'rb'), caption='<b>Ваши заказы</b>', reply_markup=await kb_user_orders(orders))


	elif cd[1] == 'show_order':
		order_id = int(cd[2])

		order_data = await db.fetchrow('SELECT * FROM orders WHERE id = $1', order_id)
		if order_data['order_status'] == 1:
			order_status = 'Completed'
		else:
			if time.time() - order_data['unix'] < 20: order_status = 'Pending'
			else:
				await call.answer('⚙️ Получаем данные заказа, это может занять несколько секунд...')
				order_status = None

			if not order_status: order_status = 'Жду ответ от сервера'

		text = f'''<b>ℹ️ Информация о заказе\n┣ 👁‍🗨 ID заказа:  <code>{order_data["order_id"]}</code>\n┣ 💈 Категория:  <code>{order_data["order_category_name"]}</code>\n┣ ⭐️ Услуга:  <code>{order_data["order_service_name"]}</code>\n┃\n┣ 🔗 Ссылка:  <code>{order_data["order_url"]}</code>\n┣ 💎 Кол-во:  <code>{order_data["order_amount"]} шт.</code>\n┣ 💰 Цена:  <code>{order_data["order_price"]} ₽</code>\n┃\n┃\n┗ {order_statuses_emoji[order_status]} Статус:  <code>{order_statuses[order_status] if order_statuses.get(order_status) else order_status}</code></b>'''

		try: msg = await call.message.edit_media(media=types.InputMediaPhoto(media=open(images['user_menu'], 'rb'), caption=text), reply_markup=await kb_user_order())
		except:
			await delmsg(call.message)
			msg = await call.message.answer_photo(photo=open(images['user_menu'], 'rb'), caption=text, reply_markup=await kb_user_order())


		if order_data['order_status'] != 1:
			order_status = (await ssf_client.get_order(order_data['order_id'])).get('status')
			if not order_status: order_status = 'Не удалось получить ответ от сервера'

			text = f'''<b>ℹ️ Информация о заказе\n┣ 👁‍🗨 ID заказа:  <code>{order_data["order_id"]}</code>\n┣ 💈 Категория:  <code>{order_data["order_category_name"]}</code>\n┣ ⭐️ Услуга:  <code>{order_data["order_service_name"]}</code>\n┃\n┣ 🔗 Ссылка:  <code>{order_data["order_url"]}</code>\n┣ 💎 Кол-во:  <code>{order_data["order_amount"]} шт.</code>\n┣ 💰 Цена:  <code>{order_data["order_price"]} ₽</code>\n┃\n┃\n┗ {order_statuses_emoji[order_status]} Статус:  <code>{order_statuses[order_status] if order_statuses.get(order_status) else order_status}</code></b>'''
			try: await msg.edit_media(media=types.InputMediaPhoto(media=open(images['user_menu'], 'rb'), caption=text), reply_markup=await kb_user_order())
			except:
				await delmsg(msg)
				await call.message.answer_photo(photo=open(images['user_menu'], 'rb'), caption=text, reply_markup=await kb_user_order())

		

	elif cd[1] == 'refill_balance': # MAIN -||- ПОПОЛНЕНИЕ БАЛАНСА
		if cd[2] == '0': #Выбор суммы для пополнения
			await states_user.refill_balance.set()
			await delmsg(call.message)
			async with state.proxy() as data:
				data['message'] = await call.message.answer(
					f'<b>💰 Пополнить баланс</b>\n<i>Введите желаемую сумму в рублях или выберите доступный вариант, нажав на кнопку</i>',
					reply_markup=await kb_refill_balancePrices())

		elif cd[2] == '1': #Выбрана сумма --> выбор платежки
			refill_amount = float(cd[3])
			try: await call.message.edit_text(f'<b>💰 Пополнить баланс</b>\nСумма:  <code>{refill_amount} ₽</code>\n\n<i>❔ Выбери способ оплаты</i>',reply_markup=await kb_payment_select(refill_amount))
			except: pass

		elif cd[2] == '2': #Выбрана платежка --> выдача формы оплаты
			refill_service = cd[3]
			refill_amount = round(float(cd[4]), 2)

			if refill_service == 'telegram':
				try:
					await bot.send_invoice(uid, title=telegram_title, description=telegram_description, provider_token=telegram_token, currency=telegram_currency, is_flexible=False, prices=[types.LabeledPrice(label='Пополнение баланса', amount=int(refill_amount*100))], payload=f'{uid}:{refill_amount}')
					return await delmsg(call.message)
				except: return await call.message.edit_text('❌ <b>Не удалось создать оплату</b> ❌', reply_markup=await kb_construct(InlineKeyboardMarkup(row_width=1), {'↪ Назад':f'cd^user:refill_balance:1:{refill_amount}'}))

			url = await payment_get_url(refill_service, refill_amount, uid)
			if refill_amount < payment_warn_limits[refill_service]:
				await call.answer(f'⚠️ При пополнении с банковских карт/сбп минимальная сумма оплаты - {payment_warn_limits[refill_service]} ₽',show_alert=True)
			elif refill_amount < payment_cancel_limits[refill_service]:
				return await call.answer(f'⚠️ Минимальная сумма пополнения данным способом - {payment_cancel_limits[refill_service]} ₽',show_alert=True)

			if not url[0]:
				return await call.message.edit_text('❌ <b>Не удалось создать оплату</b> ❌', reply_markup=await kb_construct(InlineKeyboardMarkup(row_width=1), {'↪ Назад':f'cd^user:refill_balance:1:{refill_amount}'}))

			asyncio.get_event_loop().create_task(payment_check(refill_service, refill_amount, uid, username, first_name, url[1]))
			await call.message.edit_text(
				f'<b>💰 Пополнить баланс</b>\nК оплате: <code>{refill_amount} ₽</code>\n\n<i>❔ Нажми на кнопку ниже чтобы открыть форму оплаты.\nПосле оплаты средства будут автоматически начислены на твой баланс.\n\n</i><b>❗️ ВАЖНО:</b><i> Переводите только ту сумму, что указана на странице, в противном случае средства могут быть утеряны!\n\n</i><b>☹️ Платёж не дошёл или другая проблема?</b><i>\nНапиши нам - {username_support}, приложив к сообщению скриншот чека.</i>',
				reply_markup=await kb_payment_get(refill_amount, url[2]))


	elif cd[1] == 'referal_program': # MAIN -||- РЕФЕРАЛЬНАЯ ПРОГРАММА
		ref_len, ref_profit, ref_balance = await get_ref_stats(uid)
		try: await call.message.edit_media(media=types.InputMediaPhoto(media=open(images['user_menu'], 'rb'), caption=f'<b>💙 Реферальная система 💙</b>\n\n<b>🔗 Ссылка:</b>\n<code>{bot_info["username"]}.t.me?start={uid}</code>\n<i>📘 Наша реферальная система позволит вам заработать крупную сумму без вложений. Вам необходимо лишь давать свою ссылку друзьям и вы будете получать пожизненно <code>{int(referral_percent*100)}%</code> с их пополнений в боте</i>\n\n💙 Количество рефералов:  <code>{ref_len}</code>\n🛍 Заработано с рефералов:  <code>{ref_profit} руб</code>\n💰 Баланс на вывод:  <code>{ref_balance} руб</code>'), reply_markup=await kb_ref_menu())
		except:
			await delmsg(call.message)
			await call.message.answer_photo(photo=open(images['user_menu'], 'rb'), caption=f'<b>💙 Реферальная система 💙</b>\n\n<b>🔗 Ссылка:</b>\n<code>{bot_info["username"]}.t.me?start={uid}</code>\n<i>📘 Наша реферальная система позволит вам заработать крупную сумму без вложений. Вам необходимо лишь давать свою ссылку друзьям и вы будете получать пожизненно <code>{int(referral_percent*100)}%</code> с их пополнений в боте</i>\n\n💙 Количество рефералов:  <code>{ref_len}</code>\n🛍 Заработано с рефералов:  <code>{ref_profit} руб</code>\n💰 Баланс на вывод:  <code>{ref_balance} руб</code>', reply_markup=await kb_ref_menu())

	elif cd[1] == 'request_ref_withdraw':
		ref_balance = round(float((await db.fetchrow('SELECT * FROM users WHERE uid = $1', uid))['ref_balance']), 1)
		if ref_balance < min_ref_withdraw:
			return await call.answer(f'💮 Минимальная сумма подачи на вывод {min_ref_withdraw} рублей.', show_alert=True)

		await delmsg(call.message)
		await states_user.ref_balance_withdraw.set()
		msg = await call.message.answer(f'💮 Минимальная сумма подачи на вывод  <code>{min_ref_withdraw} рублей</code>.\n💰 Баланс на вывод:  <code>{ref_balance}</code> руб\n\n<b>Введите сумму подачи на вывод</b>', reply_markup=await kb_back('user:referal_program', '❌ Отменить'))
		await state.update_data(withdraw_amount=None, ref_balance=ref_balance, msg=[msg])

	elif cd[1] == 'activate_promocode': # MAIN -||- Активация промокода/купона
		await states_user.activate_code.set()
		await delmsg(call.message)
		msg = await call.message.answer('<b>🎟 Активировать купон</b>\n<i>Теперь отправь мне купон, который ты хочешь активировать</i>', reply_markup=await kb_back('user:menu'))
		await state.update_data(msg=msg)


@dp.message_handler(state=states_user.ref_balance_withdraw)
async def states_user_ref_balance_withdraw(message: types.Message, state: FSMContext):
	mt = message.text.strip()
	uid, username, first_name = get_user(message)
	state_data = await state.get_data()
	if state_data['withdraw_amount']:
		withdraw_amount = float(state_data['withdraw_amount'])
		user_db = await db.fetchrow('SELECT * FROM users WHERE uid = $1', uid)
		await db.execute('UPDATE users SET ref_balance = $1 WHERE uid = $2', round(float(user_db['ref_balance']) - withdraw_amount, 2), uid)

		url = f'<a href="t.me/{username}">{username}</a>' if username not in ['none', None] else f'<a href="tg://user?id={uid}">{username}</a>'
		await admin_spam(f'<b>💵 Запрос на вывод</b>\n├ Пользователь: {url} (<code>{uid}</code>)\n├ Сумма вывода:  <code>{withdraw_amount} руб</code>\n└ Данные для выплаты:  <code>{mt}</code>', reply_markup=await kb_construct(InlineKeyboardMarkup(row_width=1), {'✅ Оплачено': f'cd^admin:ref_balance:{uid}:{withdraw_amount}:s', '❌ Отклонить': f'cd^admin:ref_balance:{uid}:{withdraw_amount}:c'}))
		await message.answer('<b>Запрос на вывод создан.</b>\n\nОжидание составит до 24 часов.')
		await state.finish()
		await delmsg(*state_data['msg'], message)
	else:
		try: withdraw_amount = float(mt)
		except:
			msg = await message.answer(f'<b>♦️ Введите число без посторонних символов</b>', reply_markup=await kb_back('user:referal_program', '❌ Отменить'))
			return await state.update_data(msg=[*state_data['msg'], msg])
		
		if withdraw_amount < min_ref_withdraw:
			msg = await message.answer(f'💮 Минимальная сумма подачи на вывод  <code>{min_ref_withdraw}</code> рублей.', reply_markup=await kb_back('user:referal_program', '❌ Отменить'))
			return await state.update_data(msg=[*state_data['msg'], msg])

		msg = await message.answer(f'💮 Минимальная сумма подачи на вывод  <code>{min_ref_withdraw}</code> рублей.\n\n🇷🇺 Укажите данные для выплаты: <b>Номер карты/Сбп номер/USDT-trc20/Ton</b>.', reply_markup=await kb_back('user:referal_program', '❌ Отменить'))
		await state.update_data(withdraw_amount=withdraw_amount, msg=[*state_data['msg'], msg, message])


@dp.callback_query_handler(state=states_user.ref_balance_withdraw)
async def states_user_ref_balance_withdraw_(call: types.CallbackQuery, state: FSMContext):
	await state.finish()
	return await handler_user(call, state)


# Активация промокода - ввод кода
@dp.message_handler(state=states_user.activate_code)
async def states_user_activate_code(message: types.Message, state: FSMContext):
	mt = message.text.strip()
	uid, username, first_name = get_user(message)
	user_discounts = await db.fetch('SELECT * FROM discounts WHERE (uid, discount_is_active) = ($1, True)', uid)

	async with state.proxy() as data:
		await delmsg(message, data['msg'])
		promocode_data = await db.fetchrow('SELECT * FROM promocodes WHERE promocode_id = $1', mt)

		if promocode_data is None:
			data['msg'] = await message.answer(
				'<b>⚠️ Произошла ошибка ;(</b>\n<i>Такого купона нет</i>',
				reply_markup=await kb_construct(InlineKeyboardMarkup(row_width=1),{'↪ Назад':'cd^user:menu'})
			); return

		elif promocode_data['promocode_is_active'] is False:
			data['msg'] = await message.answer(
				'<b>⚠️ Произошла ошибка ;(</b>\n<i>Купон уже был активирован максимальное кол-во раз</i>',
				reply_markup=await kb_construct(InlineKeyboardMarkup(row_width=1),{'↪ Назад':'cd^user:menu'})
			); return

		elif len(user_discounts) > 0:
			data['msg'] = await message.answer(
				'<b>⚠️ Произошла ошибка ;(</b>\n<i>У вас уже есть активный купон на скидку</i>',
				reply_markup=await kb_construct(InlineKeyboardMarkup(row_width=1),{'↪ Назад':'cd^user:menu'})
			); return

		elif len(promocode_data['promocode_activated_uids'].split(";") if promocode_data['promocode_activated_uids'] != "" else []) >= promocode_data['promocode_maxuses']:
			await db.execute('UPDATE promocodes SET promocode_is_active = False WHERE promocode_id = $1', promocode_data['promocode_id'])
			
			data['msg'] = await message.answer(
				'<b>⚠️ Произошла ошибка ;(</b>\n<i>Купон уже был активирован максимальное кол-во раз</i>',
				reply_markup=await kb_construct(InlineKeyboardMarkup(row_width=1),{'↪ Назад':'cd^user:menu'})
			); return
	
		elif str(uid) in str(promocode_data['promocode_activated_uids']):
			data['msg'] = await message.answer(
				'<b>⚠️ Произошла ошибка ;(</b>\n<i>Купон уже был активирован ранее</i>',
				reply_markup=await kb_construct(InlineKeyboardMarkup(row_width=1),{'↪ Назад':'cd^user:menu'})
			); return

	await state.finish()


	if promocode_data['promocode_type'] == 1:
		async with db.pool.acquire() as conn:
			await conn.execute('UPDATE users SET balance = balance+$1 WHERE uid = $2', promocode_data['promocode_reward'], uid)

			if len(promocode_data['promocode_activated_uids'].split(";") if promocode_data['promocode_activated_uids'] != "" else [])+1 >= promocode_data['promocode_maxuses']:
				await conn.execute('UPDATE promocodes SET (promocode_activated_uids, promocode_is_active) = ($1, False) WHERE promocode_id = $2', f"{promocode_data['promocode_activated_uids']};{uid}" if promocode_data['promocode_activated_uids'] != "" else str(uid), promocode_data['promocode_id'])
			else:
				await conn.execute('UPDATE promocodes SET promocode_activated_uids = $1 WHERE promocode_id = $2', f"{promocode_data['promocode_activated_uids']};{uid}" if promocode_data['promocode_activated_uids'] != "" else str(uid), promocode_data['promocode_id'])
	
	elif promocode_data['promocode_type'] == 2:
		async with db.pool.acquire() as conn:
			await conn.execute('INSERT INTO discounts (uid, promocode_id, discount_maxuses, discount_amount) VALUES ($1, $2, $3, $4)', uid, promocode_data['id'], promocode_data['promocode_maxuses'], promocode_data['promocode_reward'])
			await conn.execute('UPDATE promocodes SET (promocode_activated_uids, promocode_is_active) = ($1, False) WHERE promocode_id = $2', f"{promocode_data['promocode_activated_uids']};{uid}" if promocode_data['promocode_activated_uids'] != "" else str(uid), promocode_data['promocode_id'])

	url = f'<a href="t.me/{username}">{first_name}</a>' if username else f'<a href="tg://user?id={uid}">{first_name}</a>'
	if promocode_data['promocode_type'] == 1: text = f'<b>🌀 {url} (<code>{uid}</code>) активировал промокод <code>{promocode_data["promocode_id"]}</code> и получил <code>{promocode_data["promocode_reward"]} ₽</code></b>'
	elif promocode_data['promocode_type'] == 2: text = f'<b>🌀 {url} (<code>{uid}</code>) активировал промокод <code>{promocode_data["promocode_id"]}</code> и получил скидку на  <code>{promocode_data["promocode_reward"]} %</code></b>'

	await admin_spam(text)
	if promocode_data['promocode_type'] == 1:
		text = f'🌀 <b>Купон активирован</b>\n\n<i>Ваш баланс пополнен на</i> <code>{promocode_data["promocode_reward"]} ₽</code>'
	elif promocode_data['promocode_type'] == 2:
		text = f'🌀 <b>Купон активирован</b>\n\n<i>Вы получили скидку <code>{promocode_data["promocode_reward"]} %</code> на следующий заказ</i>'

	await message.answer(text, reply_markup=await kb_back('user:menu'))

@dp.callback_query_handler(state=states_user.activate_code)
async def states_user_activate_code_(call: types.CallbackQuery, state: FSMContext):
	return await handler_user(call, state)


# Пополнение баланса - выбор платежной системы
@dp.message_handler(state=states_user.refill_balance)
async def states_user_refill_balance(message: types.Message, state: FSMContext, custom_data=None):
	if custom_data is None:
		try: amount = float(message.text)
		except:
			try: await message.delete()
			except: pass
			return await state.update_data(v=await message.answer('<b>Отправьте только число</b>'))

		async with state.proxy() as data:
			if 'v' in data:
				try: await data['v'].delete()
				except Exception as e: logging.error(e)

			try: await data['message'].delete()
			except: pass
			await state.finish()
	else: amount = float(custom_data)
	amount = round(amount, 2)

	try: await message.delete()
	except: pass
	await message.answer(f'<b>💰 Пополнить баланс</b>\nСумма:  <code>{amount} ₽</code>\n<i>❔ Выбери способ оплаты</i>',reply_markup=await kb_payment_select(amount))

@dp.callback_query_handler(state=states_user.refill_balance)
async def states_user_refill_balance_(call: types.CallbackQuery, state: FSMContext):
	return await handler_user(call, state)

# Пополнение баланса - telegram ==> pre-checkout
@dp.pre_checkout_query_handler(lambda query: True)
async def payment_telegram_pre_checkout(pre_checkout_q: types.PreCheckoutQuery):
	logging.debug(f'Pre checkout: {pre_checkout_q}')
	await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)

@dp.message_handler(content_types=types.message.ContentType.SUCCESSFUL_PAYMENT)
async def payment_telegram_success(message: types.Message, state: FSMContext):
	uid, username, first_name = get_user(message)
	payment_service = 'telegram'
	payment_info = message.successful_payment
	unix = int(time.time())
	invoce_id = f'{uid}:{unix}:{random.randint(111,999)}'

	referral_from_id = (await db.fetchrow('SELECT referral_from_id FROM users WHERE uid = $1', uid))['referral_from_id']
	amount = round(payment_info.total_amount / 100, 2)

	await db.execute('INSERT INTO transactions_refill(transaction_id, uid, issue_date, payment_service_name, payment_amount) VALUES ($1, $2, $3, $4, $5)', invoce_id, uid, unix, payment_service, amount)
	if referral_from_id:
		referral_amount = round(amount*referral_percent, 2)
		db_referral_from_id = await db.fetchrow('SELECT * FROM users WHERE uid = $1', referral_from_id)
		await db.execute('UPDATE users SET balance = balance+$1 WHERE uid = $2', referral_amount, referral_from_id)
		
		url = f'<a href="t.me/{username}">{first_name}</a>' if username else f'<a href="tg://user?id={uid}">{first_name}</a>'
		try: await bot.send_message(referral_from_id, f'<b>💰 Ваш реферал {url} пополнил баланс на сумму</b> <code>{amount} ₽</code>\n<b>📃 Вы получили</b> <code>{referral_amount} ₽</code>', reply_markup=await kb_construct(InlineKeyboardMarkup(row_width=1), {'❌ Закрыть':'cd^utils:delete'}), disable_web_page_preview=True)
		except: pass
		referral_from_id_username = db_referral_from_id['username']
		url = f'<a href="t.me/{referral_from_id_username}">{referral_from_id_username}</a>' if referral_from_id_username not in ['none', None] else f'<a href="tg://user?id={referral_from_id}">{referral_from_id_username}</a>'
		await admin_spam(f'<b>💰 Пользователь {url} (<code>{referral_from_id}</code>) получил с реферала <code>{referral_amount} ₽</code></b>')

	await admin_spam(f'<b>{payment_service.capitalize()}</b>\n<i>Пользователь:</i> <b>@{username} | <code>{uid}</code></b>\n<i>Сумма пополнения:</i> <code>{amount} ₽</code>')
	await db.execute('UPDATE users SET balance = balance+$1 WHERE uid = $2', amount, uid)
	try: await bot.send_message(uid, f'<b>🌀 Ваш баланс пополнен на сумму  <code>{amount} ₽</code></b>', reply_markup=await kb_construct(InlineKeyboardMarkup(row_width=1), {'❌ Закрыть':'cd^utils:delete'}))
	except: pass

	return await handler_text(message, state, custom_data='👤 Профиль')


	
##################################!!! HANDLERS - SMM - HANDLERS !!!#############################################################
class states_smm(StatesGroup):
	add_creds = State()

@dp.message_handler(text='⭐️ Заказать накрутку')
async def smm_start_message(message: types.Message, state: FSMContext):
	await message.answer_photo(photo=open(images['smm_menu'], 'rb'), caption='<i>💈 Выберите категорию накрутки:</i>', reply_markup=await kb_get_categories())


@dp.callback_query_handler(text_startswith='smm')
async def handler_smm(call: types.CallbackQuery, state: FSMContext, custom_data=None):
	await state.finish()
	cd = custom_data.split(':') if custom_data else call.data.split(':')
	uid, username, first_name = get_user(call)
	ts = int(time.time())


	if cd[1] == 'menu':
		page_id = int(cd[2]) if len(cd) > 3 else 1
		prefix = cd[3] if len(cd) == 4 and cd[3] != 'None' else ''

		try: await call.message.edit_media(media=types.InputMediaPhoto(media=open(images['smm_menu'], 'rb'), caption='<i>💈 Выберите категорию накрутки:</i>'), reply_markup=await kb_get_categories(page=page_id, prefix=prefix))
		except:
			await delmsg(call.message)
			await call.message.answer_photo(photo=open(images['smm_menu'], 'rb'), caption='<i>💈 Выберите категорию накрутки:</i>', reply_markup=await kb_get_categories(page=page_id, prefix=prefix))

	elif cd[1] == 'c':
		category_name = cd[2]
		page_id = int(cd[3])

		if category_name.startswith('__main'):
			prefix = category_name[-3:-2]
			
			try: await call.message.edit_media(media=types.InputMediaPhoto(media=open(images['smm_menu'], 'rb'), caption='<i>💈 Выберите категорию накрутки:</i>'), reply_markup=await kb_get_categories(page=page_id, prefix=prefix))
			except:
				await delmsg(call.message)
				await call.message.answer_photo(photo=open(images['smm_menu'], 'rb'), caption='<i>💈 Выберите категорию накрутки:</i>', reply_markup=await kb_get_categories(page=page_id, prefix=prefix))
			return


		text = f'<i>🌐 Выберите тип услуги:</i>\n┗ Категория:  <code>{sets_categories[category_name]}</code>'
		kb = await kb_get_categories(category_name, page=page_id, prefix=category_name[0] if not cpf(category_name) else None)

		try: await call.message.edit_media(media=types.InputMediaPhoto(media=open(images['smm_menu'], 'rb'), caption=text), reply_markup=kb)
		except:
			await delmsg(call.message)
			await call.message.answer_photo(photo=open(images['smm_menu'], 'rb'), caption=text, reply_markup=kb)

	elif cd[1] == 'ct':
		category_name = cd[2]
		category_type_hash = cd[3]
		page_id = int(cd[4])

		try:
			x = ssf_client.all_data['category_type_hash'].get(f'{rpf(category_name)}_{category_type_hash}')
			text = f'<i>🌐 Выберите услугу:</i>\n┣ Категория:  <code>{sets_categories[category_name]}</code>\n┗ Тип:  <code>{x}</code>'
			kb = await kb_get_categories(category_name, category_type_hash, page=page_id)

			try: await call.message.edit_media(media=types.InputMediaPhoto(media=open(images['smm_menu'], 'rb'), caption=text), reply_markup=kb)
			except:
				await delmsg(call.message)
				await call.message.answer_photo(photo=open(images['smm_menu'], 'rb'), caption=text, reply_markup=kb)
		except:
			await call.answer('⚠️ Неизвестная ошибка, попробуйте позже', show_alert=True)

	elif cd[1] == 'cs':
		category_name = cd[2]
		category_type_hash = cd[3]
		service_id = cd[4]
		page_id = int(cd[5])
		
		services = await ssf_client.get_services(True)
		service_data = services[rpf(category_name)][category_type_hash][service_id]

		x = ssf_client.all_data['category_type_hash'].get(f'{rpf(category_name)}_{category_type_hash}')

		discount = await get_discount(uid)
		price_ = await round_to_precision(service_data["price"] + (service_data["price"] * extra_price_percent))
		price_po = await round_to_precision(service_data["price"] * 1000 + ((service_data["price"] * 1000) * extra_price_percent))
		if discount:
			price_d = await round_to_precision(price_ - price_ * discount["discount_amount"]/100)
			price_pod = await round_to_precision(price_po - price_po * discount["discount_amount"]/100)
			price_text = f'<b>💥 Цена за 1 шт:</b>  <s>{price_} ₽</s>  <code>{price_d} ₽</code> (скидка <code>{discount["discount_amount"]}%</code>)\n<b>💥 Цена за 1000 шт:</b>  <s>{price_po} ₽</s>  <code>{price_pod} ₽</code> (скидка <code>{discount["discount_amount"]}%</code>)'
		else: price_text = f'<b>💥 Цена за 1 шт:</b>  <code>{price_} ₽</code>\n<b>💥 Цена за 1000 шт:</b>  <code>{price_po} ₽</code>'
		text = f'''<b>🛒 Создание заказа</b>\n┣ Категория:  <b>{sets_categories[category_name]}</b>\n┗ Услуга:  <code>{service_data["name"]}</code>\n\n\n{price_text}\n\n<b>❗️ Минимальное кол-во:</b>  <code>{service_data["min"]} шт.</code>\n<b>💢 Максимальное кол-во:</b>  <code>{service_data["max"]} шт.</code>\n\n<b>Описание:</b>\n<i>{service_data["description"] if service_data.get('description') and service_data.get('description') != "" else "Время выполнения заказа 1-30мин. Работает для всех каналов!"}</i>'''

		try: await call.message.edit_text(text, reply_markup=await kb_get_category_types(category_name, category_type_hash, service_data['service_id'], page=page_id))
		except:
			await delmsg(call.message)
			await call.message.answer(text, reply_markup=await kb_get_category_types(category_name, category_type_hash, service_data['service_id'], page=page_id))

	elif cd[1] == 'b':
		category_name = cd[2]
		category_type_hash = cd[3]
		service_id = cd[4]
		page_id = int(cd[5])
		await states_smm.add_creds.set()
		
		services = await ssf_client.get_services(True)
		service_data = services[rpf(category_name)][category_type_hash][service_id]

		x = ssf_client.all_data['category_type_hash'].get(f'{rpf(category_name)}_{category_type_hash}')
		msg = await call.message.edit_text(f'<b>🛒 Создание заказа\n┣ Категория:  <code>{sets_categories[category_name]}</code>\n┣ Услуга:  <code>{service_data["name"]}</code>\n\n\n ❗️ДЛЯ ОФОРМЛЕНИЯ ЗАКАЗА УКАЖИТЕ ОТКРЫТУЮ ССЫЛКУ, без слова boost.\n(Например https://t.me/+4V18dXn4ojJiNTFi или https://t.me/boostmca).</b>', reply_markup=await kb_construct(InlineKeyboardMarkup(), {'↪ Назад': f'cd^smm:cs:{category_name}:{category_type_hash}:{service_id}:{page_id}'}))
		await state.update_data(msg=msg, category_name=category_name, category_type_hash=category_type_hash, service_id=service_id, page_id=page_id, service_data=service_data, x=x, state='url')

	elif cd[1] == 'by':
		if len(cd) == 3:
			await call.answer('⚠️ Что-то пошло не так, попробуйте позже. ⚠️', show_alert=True)
			return await handler_smm(call, state, 'smm:menu')
		
		return await handler_smm(call, state, f'smm:b:{category_name}:{category_type_hash}:{service_id}:{page_id}')


@dp.message_handler(state=states_smm.add_creds)
async def states_smm_add_creds(message: types.Message, state: FSMContext):
	mt = message.text.strip()
	uid, username, first_name = get_user(message)
	state_data = await state.get_data()

	if state_data['state'] == 'url':
		await delmsg(state_data['msg'], message)
		if not mt.startswith('https://'):	
			msg = await message.answer('<b>❌ Ссылка должна начинаться с <code>https://</code>! Попробуйте еще раз.</b>', reply_markup=await kb_construct(InlineKeyboardMarkup(), {'↪ Назад': f'cd^smm:cs:{state_data["category_name"]}:{state_data["category_type_hash"]}:{state_data["service_id"]}:{state_data["page_id"]}'}))
			return await state.update_data(msg=msg)
		
		msg = await message.answer(f'<b>🛒 Создание заказа\n┗ 🔗 Ссылка:  <code>{mt}</code></b>\n\n\n<b>❗️ ВВЕДИТЕ КОЛЛИЧЕСТВО</b> <b>(от <code>{state_data["service_data"]["min"]}</code> до <code>{state_data["service_data"]["max"]}</code>)</b>', reply_markup=await kb_construct(InlineKeyboardMarkup(), {'↪ Назад': f'cd^smm:cs:{state_data["category_name"]}:{state_data["category_type_hash"]}:{state_data["service_id"]}:{state_data["page_id"]}'}))
		await state.update_data(msg=msg, url=mt, state='amount')

	elif state_data['state'] == 'amount':
		await delmsg(state_data['msg'], message)
		if not mt.isnumeric():
			msg = await message.answer('<b>❌ Количество должно быть целым числом! Попробуйте еще раз.</b>', reply_markup=await kb_construct(InlineKeyboardMarkup(), {'↪ Назад': f'cd^smm:cs:{state_data["category_name"]}:{state_data["category_type_hash"]}:{state_data["service_id"]}:{state_data["page_id"]}'}))
			return await state.update_data(msg=msg)
		amount = int(mt)

		if amount < int(state_data["service_data"]["min"]) or amount > int(state_data["service_data"]["max"]):
			msg = await message.answer(f'<b>❌ Количество должно быть в диапазоне от <code>{state_data["service_data"]["min"]}</code> до <code>{state_data["service_data"]["max"]}</code> включительно! Попробуйте еще раз.</b>', reply_markup=await kb_construct(InlineKeyboardMarkup(), {'↪ Назад': f'cd^smm:cs:{state_data["category_name"]}:{state_data["category_type_hash"]}:{state_data["service_id"]}:{state_data["page_id"]}'}))
			return await state.update_data(msg=msg)
		

		orig_price_per_one = float(state_data["service_data"]["price"])
		orig_price = await round_to_precision(orig_price_per_one * amount)
		price_per_one = await round_to_precision(orig_price_per_one + (orig_price_per_one * extra_price_percent))
		price = round(await round_to_precision(price_per_one * amount), 2)

		price_text = f'<code>{price} ₽</code>'

		discount = await get_discount(uid)
		if discount:
			last_price = price
			price_per_one = await round_to_precision(price_per_one - (price_per_one * discount["discount_amount"]/100))
			price = await round_to_precision(price - (price * discount["discount_amount"]/100))
			price_text = f'<s>{last_price} ₽</s>  <code>{price} ₽</code> (скидка <code>{discount["discount_amount"]}%</code>)'


		services = await ssf_client.get_services(True)
		service_data = services[rpf(state_data['category_name'])][state_data['category_type_hash']][state_data['service_id']]

		msg = await message.answer(f'<b>🛒 Создание заказа\n┣ Категория:  <code>{sets_categories[state_data["category_name"]]}</code>\n┣ Тип:  <code>{state_data["x"]}</code>\n┣ Услуга:  <code>{service_data["name"]}</code>\n┃\n┣ 🔗 Ссылка:  <code>{state_data["url"]}</code>\n┣ 💎 Кол-во:  <code>{amount} шт.</code>\n┗ 💰 Цена:  {price_text}</b>\n\n\n<b>❗️ Проверьте данные перед покупкой</b>', reply_markup=await kb_construct(InlineKeyboardMarkup(row_width=1), {'💎 Заказать': f'cd^smm:by:{state_data["service_id"]}', '↪ Назад': f'cd^smm:cs:{state_data["category_name"]}:{state_data["category_type_hash"]}:{state_data["service_id"]}:{state_data["page_id"]}'}))
		await state.update_data(msg=msg, state='confirm', orig_price_per_one=orig_price_per_one, orig_price=orig_price, price_per_one=price_per_one, price=price, amount=amount)

	elif state_data['state'] == 'confirm':
		return await delmsg(message)


@dp.callback_query_handler(state=states_smm.add_creds)
async def states_smm_add_creds(call: types.CallbackQuery, state: FSMContext):
	uid, username, first_name = get_user(call)
	state_data = await state.get_data()
	await state.finish()

	discount = await get_discount(uid)
	if state_data['state'] == 'confirm' and call.data.startswith('smm:by:'):
		if state_data['price'] == 0 and not (discount and discount['discount_amount'] == 100):
			return await call.message.edit_text(f'🤔 <b>Подозрительный ценник</b>\nМы проверим данный сервис в течении нескольких часов, <i>на протяжении этого времени данный сервис будет недоступен, приносим свои извинения.</i>', reply_markup=await kb_construct(InlineKeyboardMarkup(), {'↪ Назад': f'cd^smm:cs:{state_data["category_name"]}:{state_data["category_type_hash"]}:{state_data["service_id"]}:{state_data["page_id"]}'}))
		user_db = await db.fetchrow('SELECT * FROM users WHERE uid = $1', uid)
		if state_data['price'] > 0 and user_db['balance'] < state_data['price']: return await call.message.edit_text('<b>❌ Недостаточно средств на балансе.</b>', reply_markup=await kb_construct(InlineKeyboardMarkup(row_width=1), {'💰 Пополнить баланс': f'cd^user:refill_balance:1:{state_data["price"] - user_db["balance"]}', '↪ Назад': f'cd^smm:cs:{state_data["category_name"]}:{state_data["category_type_hash"]}:{state_data["service_id"]}:{state_data["page_id"]}'}))
		
		await call.answer('⚙️ Создаем заказ, это может занять несколько секунд...', show_alert=True)
		task = await smm_create_task(uid, {'url': state_data['url'], 'amount': state_data['amount'], 'orig_price': state_data['orig_price'], 'orig_price_per_one': state_data['orig_price_per_one'], 'price': state_data['price'], 'price_per_one': state_data['price_per_one'], 'category_name': state_data['category_name'], 'category_type_hash': state_data['category_type_hash'], 'service_id': state_data['service_id']})
		if task['status']:
			return await handler_user(call, state, f'user:show_order:{task["order_id"]}')
		else: await call.message.edit_text(f'<b>❌ Не удалось создать заказ ❌</b>\n\n<b>Причина:</b> {task["msg"]}', reply_markup=await kb_construct(InlineKeyboardMarkup(), {'↪ Назад': f'cd^smm:cs:{state_data["category_name"]}:{state_data["category_type_hash"]}:{state_data["service_id"]}:{state_data["page_id"]}'}))
	else: await handler_smm(call, state)


##################################!!! HANDLERS - ADMIN - HANDLERS !!!############################################################
class states_admin(StatesGroup):
	spam_create_session = State()
	spam_add_media = State()
	spam_confirm = State()

	search_user = State()
	change_balance = State()

	ban_reason_set = State()
	ban_time_set = State()

	find_receipt = State()
	create_promocode = State()
	refund_custom = State()


@dp.callback_query_handler(text_startswith='admin')
async def handler_admin(call: types.CallbackQuery, state: FSMContext, custom_data = None):
	await state.finish()
	cd = custom_data.split(':') if custom_data else call.data.split(':')

	
	
	uid, username, first_name = get_user(call)
	if uid not in admin_ids: return

	if cd[1] == 'menu':
		try: await call.message.edit_text('<b>🧑🏻‍💻 Админ меню</b>', reply_markup=await kb_admin_menu())
		except: 
			try: await call.message.delete()
			except: pass
			await call.message.answer('<b>🧑🏻‍💻 Админ меню</b>', reply_markup=await kb_admin_menu())

	elif cd[1] == 'orders':
		target_uid = int(cd[2])

		if len(cd) == 3:
			target_user = await db.fetchrow('SELECT * FROM users WHERE uid = $1', target_uid)
			orders = await db.fetch('SELECT * FROM orders WHERE uid = $1', target_uid)

			if len(orders) == 0: return await call.answer('У пользователя нет заказов', show_alert=True)
			await call.message.edit_text(f'<b>Заказы пользователя {format_user_url(user_db=target_user)} (<code>{target_uid}</code>)</b>', reply_markup=await kb_user_orders(orders, target_uid), disable_web_page_preview=True)
		
		elif len(cd) == 4:
			target_user = await db.fetchrow('SELECT * FROM users WHERE uid = $1', target_uid)
			order_id = int(cd[3])
			order_data = await db.fetchrow('SELECT * FROM orders WHERE id = $1', order_id)
			if time.time() - order_data['unix'] < 20: order_status = 'Pending'
			else:
				await call.answer('⚙️ Получаем данные заказа, это может занять несколько секунд...')
				order_status = None
			if not order_status: order_status = 'Жду ответ от сервера'

			text = f'''<b>ℹ️ Информация о заказе\n┣ 👁‍🗨 ID заказа:  <code>{order_data["order_id"]}</code>\n┣ 💈 Категория:  <code>{order_data["order_category_name"]}</code>\n┣ ⭐️ Услуга:  <code>{order_data["order_service_name"]}</code>\n┣ 🆔 Пользователь:  {format_user_url(user_db=target_user)} (<code>{target_uid}</code>)\n┃\n┣ 🔗 Ссылка:  <code>{order_data["order_url"]}</code>\n┣ 💎 Кол-во:  <code>{order_data["order_amount"]} шт.</code>\n┣ 💰 Цена:  <code>{order_data["order_price"]} ₽</code>\n┃\n┃\n┗ {order_statuses_emoji[order_status]} Статус:  <code>{order_statuses[order_status] if order_statuses.get(order_status) else order_status}</code></b>'''

			msg = await call.message.edit_text(text, reply_markup=await kb_user_order(target_uid), disable_web_page_preview=True)
			order_status = (await ssf_client.get_order(order_data['order_id'])).get('status')
			if not order_status: order_status = 'Не удалось получить ответ от сервера'

			text = f'''<b>ℹ️ Информация о заказе\n┣ 👁‍🗨 ID заказа:  <code>{order_data["order_id"]}</code>\n┣ 💈 Категория:  <code>{order_data["order_category_name"]}</code>\n┣ ⭐️ Услуга:  <code>{order_data["order_service_name"]}</code>\n┣ 🆔 Пользователь:  {format_user_url(user_db=target_user)} (<code>{target_uid}</code>)\n┃\n┣ 🔗 Ссылка:  <code>{order_data["order_url"]}</code>\n┣ 💎 Кол-во:  <code>{order_data["order_amount"]} шт.</code>\n┣ 💰 Цена:  <code>{order_data["order_price"]} ₽</code>\n┃\n┃\n┗ {order_statuses_emoji[order_status]} Статус:  <code>{order_statuses[order_status] if order_statuses.get(order_status) else order_status}</code></b>'''
			await msg.edit_text(text, reply_markup=await kb_user_order(target_uid), disable_web_page_preview=True)

	elif cd[1] == 'ref_balance':
		act = cd[4]
		target_uid = int(cd[2])
		withdraw_amount = float(cd[3])

		if act == 's':
			try: await bot.send_message(target_uid, f'<b>✅ Запрос на вывод выполнен</b>')
			except: pass
			await call.answer('✅ Запрос на вывод выполнен', show_alert=True)
		elif act == 'c':
			user_db = await db.fetchrow('SELECT * FROM users WHERE uid = $1', target_uid)
			await db.execute('UPDATE users SET ref_balance = ref_balance + $1 WHERE uid = $2', round(float(user_db['ref_balance']) + withdraw_amount, 2), target_uid)
			try: await bot.send_message(target_uid, f'<b>❌ Запрос на вывод отклонён</b>')
			except: pass
			await call.answer('❌ Запрос на вывод отклонён', show_alert=True)
		
		await delmsg(call.message)

	elif cd[1] == 'spam_create':
		if len(cd) == 2:
			return await call.message.edit_text('<i>📨 Выберите тип рассылки</i>',reply_markup=await kb_spam())

		await states_admin.spam_create_session.set()
		async with state.proxy() as data:
			data['spam_type'] = cd[2]
			data['message'] = await call.message.edit_text('<b>📨 Отправьте текст для рассылки</b>', reply_markup=await kb_back('admin:spam_create'))

	elif cd[1] == 'search_user':
		await states_admin.search_user.set()
		async with state.proxy() as data:
			data['message'] = await call.message.edit_text(
				'🌐 Отправьте <b>ID</b> или <b>юзернейм пользователя</b>',
				reply_markup=await kb_construct(InlineKeyboardMarkup(row_width=2),{'↪ Назад':'cd^admin:menu'})
			)

	elif cd[1] == 'change_balance':
		await states_admin.change_balance.set()
		async with state.proxy() as data:
			user_balance = await db.fetchrow('SELECT balance FROM users WHERE uid = $1', cd[2])['balance']
			data['uid'] = int(cd[2])
			data['is_add'] = 0
			data['balance'] = user_balance
			data['message'] = await call.message.edit_text(
				f'<b>Введите новый баланс пользователя\n\nТекущий баланс: <code>{round(user_balance, 3)} ₽</code></b>',
				reply_markup=await kb_construct(InlineKeyboardMarkup(row_width=1),
					{
						'✅ Добавить баланс ✅':f'cd^admin:menu:False:{user_balance}',
						'↪ Назад':f'cd^temp:finduser:{cd[2]}'
					}
				)
			)

	elif cd[1] == 'ban':
		user_uid = int(cd[3])
		if cd[2] == '0': 
			await db.execute('UPDATE users SET is_banned = False WHERE uid = $1', user_uid)
			await db.execute('DELETE FROM banned WHERE uid = $1', user_uid)
			

			await call.answer('❎ Пользовать разблокирован ❎')
			try: await bot.send_message(int(cd[3]),'<b>Вы были разблокированы.</b>\n<i>Приятного пользования, не нарушайте правила!</i>')
			except: pass
			return await handler_temp(call, state, f'temp:finduser:{user_uid}')

		elif cd[2] == '1':
			await states_admin.ban_reason_set.set()

			async with state.proxy() as data:
				data['uid'] = user_uid
				data['message'] = await call.message.edit_text(f'<b>Введите причину блокировки пользователя</b>',reply_markup=await kb_construct(InlineKeyboardMarkup(row_width=1),{'Без причины':f'cd^admin:menu:{user_uid}','↪ Назад':f'cd^temp:finduser:{user_uid}'}))

	elif cd[1] == 'stats':
		up_all, up_24h, all_bal, all_up, users, users_sub = 0, 0, 0, 0, 0, 0

		up_all = await db.fetchrow('SELECT COUNT(*) AS a, COALESCE(SUM(payment_amount), 0) AS m FROM transactions_refill')
		up_24h = await db.fetchrow('SELECT COUNT(*) AS a, COALESCE(SUM(payment_amount), 0) AS m FROM transactions_refill WHERE issue_date >= $1', int(time.time())-86400)
		
		sells_all = await db.fetchrow('SELECT COUNT(*) AS a, COALESCE(SUM(order_price), 0) AS m FROM orders')
		income_all = await db.fetchrow('SELECT COUNT(*) AS a, COALESCE(SUM(order_price - order_orig_price), 0) AS m FROM orders')
		all_bal = (await db.fetchrow('SELECT COALESCE(SUM(balance), 0) as q FROM users WHERE balance > 0'))['q']
		users = (await db.fetchrow('SELECT COALESCE(COUNT(id), 0) as q FROM users'))['q']

		text = f'''<b>📊 СТАТИСТИКА БОТА</b>\n➖➖➖➖➖➖➖➖➖➖\n🖥 Баланс панели:  <code>Жду ответ от сервера</code>\n\n👤 Пользователей за Всё время:  <code>{users}</code>\n💸 Продаж за Всё время:  <code>{sells_all["a"]} шт — {round(sells_all["m"], 2)} ₽</code>\n💰 Пополнений за День:  <code>{up_24h["a"]} шт — {round(up_24h["m"], 2)} ₽</code>\n💰 Пополнений за Всё время:  <code>{up_all["a"]} шт — {round(up_all["m"], 2)} ₽</code>\n\n💵 Прибыль за Всё время:  <code>{income_all["a"]} шт — {round(income_all["m"], 2)} ₽</code>\n💳 Средств в системе:  <code>{round(all_bal, 2)} ₽</code>'''
		msg = await call.message.edit_text(text=text, reply_markup=await kb_back('admin:menu'))#f'<b>🔶 Средства 🔶</b>\n📕 Пополнений за 24 часа:  <code>{up_24h} ₽</code>\n💳 Средств в системе:  <code>{round(all_bal, 3)} ₽</code>\n🥝 Пополнено:  <code>{all_up} ₽</code>\n\n🌀 <b>Общее</b> 🌀\n👶🏿 Пользователей:  <code>{users}</code>'
		balance = await ssf_client.get_balance()

		text = f'''<b>📊 СТАТИСТИКА БОТА</b>\n➖➖➖➖➖➖➖➖➖➖\n🖥 Баланс панели:  <code>{str(balance.get("balance")) + " ₽" if balance.get("balance") is not None else "Не удалось получить ответ от сервера"}</code>\n\n👤 Пользователей за Всё время:  <code>{users}</code>\n💸 Продаж за Всё время:  <code>{sells_all["a"]} шт — {round(sells_all["m"], 2)} ₽</code>\n💰 Пополнений за День:  <code>{up_24h["a"]} шт — {round(up_24h["m"], 2)} ₽</code>\n💰 Пополнений за Всё время:  <code>{up_all["a"]} шт — {round(up_all["m"], 2)} ₽</code>\n\n💵 Прибыль за Всё время:  <code>{income_all["a"]} шт — {round(income_all["m"], 2)} ₽</code>\n💳 Средств в системе:  <code>{round(all_bal, 2)} ₽</code>'''
		try: await msg.edit_text(text, reply_markup=await kb_back('admin:menu'))
		except: pass

	elif cd[1] == 'all_banned':
		await call.message.edit_text(f'<i>Всего заблокированных пользователей:</i> <code>{len(await db.fetch("SELECT id FROM users WHERE is_banned = True"))}</code>', reply_markup=await kb_admin_banned_users())

	elif cd[1] == 'find_receipt':
		return await call.answer('⚙️ Иди поспи')
		await states_admin.find_receipt.set()
		async with state.proxy() as data:
			data['message'] = await call.message.edit_text('🌐 Отправьте <b>ID</b> чека',reply_markup=await kb_back('admin:menu'))

	elif cd[1] == 'promocode': # Типы промокодов: {1: Деньги, 2: Скидка в %}
		# Меню
		if len(cd) == 2:
			await call.message.edit_text('<b>Выберите действие</b>', reply_markup=await kb_admin_promocode())
		
		elif len(cd) == 3:
			act = cd[2]

			if act == 'c':
				await call.message.edit_text('<b>Создание промокода</b>\n\nВыберите тип промокода', reply_markup=await kb_admin_promocode_create('type'))
			elif act == 'g':
				
				

				promocodes_ = await db.fetch('SELECT * FROM promocodes WHERE promocode_is_active = True')
				promocodes = []
				if len(promocodes_) < 10:
					for x in promocodes_:
						if x["promocode_type"] == 1: promocodes.append(f'<code>{x["promocode_id"]}</code> --> Uses: <i>{len(x["promocode_activated_uids"].split(";")) if x["promocode_activated_uids"] != "" else 0}/{x["promocode_maxuses"]}</i> | Reward: <code>{x["promocode_reward"]} ₽</code>')
						elif x['promocode_type'] == 2: promocodes.append(f'<code>{x["promocode_id"]}</code> --> Uses: <i>{len(x["promocode_activated_uids"].split(";")) if x["promocode_activated_uids"] != "" else 0}/{x["promocode_maxuses"]}</i> | Reward: <code>{x["promocode_reward"]} %</code>')
					promocodes = '\n'.join(promocodes)
					
					await call.message.edit_text(f'🌀 Активных промокодов: <b><code>{len(promocodes_)}</code> шт.</b>\n\n{promocodes}',reply_markup=await kb_back('admin:promocode'))
				else:
					await call.answer('⚙️ Выгружаю...')
					for x in promocodes_:
						if x["promocode_type"] == 1: promocodes.append(f'{x["promocode_id"]} --> Uses: {len(x["promocode_activated_uids"].split(";")) if x["promocode_activated_uids"] != "" else 0}/{x["promocode_maxuses"]} | Reward: {x["promocode_reward"]} ₽')
						elif x['promocode_type'] == 2: promocodes.append(f'{x["promocode_id"]} --> Uses: {len(x["promocode_activated_uids"].split(";")) if x["promocode_activated_uids"] != "" else 0}/{x["promocode_maxuses"]} | Reward: {x["promocode_reward"]} %')
					promocodes = '\n'.join(promocodes)

					f_name = f'Active promocodes #{random.randint(111,999)}.txt'
					open(f_name, 'w', encoding='utf-8').write(promocodes)
					await call.message.answer_document(open(f_name,'rb'), caption=f'🌀 Активных промокодов: <b><code>{len(promocodes_)}</code> шт.</b>', reply_markup=await kb_close())
					threading.Thread(target=os_delete,args=[f_name]).start()

		elif len(cd) == 4:
			act = cd[2]
			promocode_type = int(cd[3])

			if act == 'c':
				await states_admin.create_promocode.set()
				msg = await call.message.edit_text(f'<b>Создание промокода</b>\n┗ Тип промокода:  <code>{promocode_types[promocode_type]}</code>\n\n<b>Отправьте вознаграждение за промокод</b>' if promocode_type == 1 else f'<b>Создание промокода</b>\n┗ Тип промокода:  <code>{promocode_types[promocode_type]}</code>\n\n<b>Отправьте скидку в процентах (от <code>1</code> до <code>100</code>)</b>', reply_markup=await kb_admin_promocode_create('reward'))
				await state.update_data(msg=msg, promocode_type=promocode_type, state='reward')

			elif act == 'r':
				reward = float(cd[4])

				await states_admin.create_promocode.set()
				msg = await call.message.edit_text(f'<b>Создание промокода</b>\n┣ Тип промокода:  <code>{promocode_types[promocode_type]}</code>\n┗ Вознаграждение:  <code>{reward}</code>\n\n<b>Отправьте количество создаваемых промокодов</b>' if promocode_type == 1 else f'<b>Создание промокода</b>\n┣ Тип промокода:  <code>{promocode_types[promocode_type]}</code>\n┗ Скидка:  <code>{reward}</code>\n\n<b>Отправьте количество использований</b>', reply_markup=await kb_admin_promocode_create('uses_amount'))
				await state.update_data(msg=msg, promocode_type=promocode_type, reward=reward, state='uses_amount')

	elif cd[1] == 'refund':
		order_id = int(cd[2])
		act = cd[3]

		order_db = await db.fetchrow('SELECT * FROM orders WHERE order_id = $1', order_id)
		if order_db['order_status'] in (1, 2):
			return await call.answer('Средства за заказ уже возвращены', show_alert=True)

		if act == 'accept':
			if len(cd) == 4: order_price = order_db['order_price']
			else: order_price = float(cd[4])
			await db.execute('UPDATE users SET balance = balance + $1 WHERE uid = $2', order_price, order_db['uid'])
			await db.execute('UPDATE orders SET order_status = 2 WHERE order_id = $1', order_id)
			
			try: await bot.send_message(order_db['uid'], f'<b>📃 Ваш заказ <code>{order_id}</code> был отменён, средства в размере <code>{order_price} ₽</code> возращены</b>.', reply_markup=await kb_construct(InlineKeyboardMarkup(row_width=1), {'❌ Закрыть':'cd^utils:delete'}), disable_web_page_preview=True)
			except: pass
			user_db = await db.fetchrow('SELECT * FROM users WHERE uid = $1', order_db['uid'])
			await admin_spam(f'<b>📃 Пользователь {format_user_url(user_db=user_db)}|<code>{user_db["uid"]}</code> получил возврат средств за заказ <code>{order_id}</code> в размере <code>{order_price} ₽</code></b>')
			await call.answer('Статус заказа изменён', show_alert=True)
			await delmsg(call.message)
		elif act == 'custom':
			await call.message.answer(f'<b>Отправьте сумму возврата за заказ <code>{order_id}</code></b>', reply_markup=await kb_construct(InlineKeyboardMarkup(row_width=1), {'❌ Отмена': 'cd^admin:menu'}))
			await states_admin.refund_custom.set()
			await state.update_data(order_id=order_id)
			await call.answer('')
		else:
			await db.execute('UPDATE orders SET order_status = 1 WHERE order_id = $1', order_id)
			
			await call.answer('Статус заказа изменён', show_alert=True)
			await delmsg(call.message)



@dp.message_handler(state=states_admin.refund_custom)
async def states_admin_refund_custom(message: types.Message, state: FSMContext):
	mt = message.text
	try: order_price = float(mt)
	except: return await message.answer('Введите число без посторонних символов ❗️', reply_markup=await kb_close())
	state_data = await state.get_data()

	order_id = state_data['order_id']
	print(order_id)
	await state.finish()
	await message.answer(f'<b>ID заказа: <code>{order_id}</code>\nСумма возврата: <code>{order_price} ₽</code></b>', reply_markup=await kb_construct(InlineKeyboardMarkup(row_width=1), {'✅ Вернуть средства': f'cd^admin:refund:{order_id}:accept:{order_price}', '❌ Отмена': 'cd^utils:delete'}))


@dp.callback_query_handler(state=states_admin.refund_custom)
async def states_admin_refund_custom_(call: types.CallbackQuery, state: FSMContext):
	await state.finish()
	await delmsg(call.message)


# Админ панель - Поиск пользователя
@dp.message_handler(state=states_admin.search_user)
async def states_admin_search_user(message: types.Message, state: FSMContext, custom_data = None):
	
	
	async with state.proxy() as data:

		if custom_data is None:
			try:
				await data['message'].delete()
				await message.delete()
			except: pass
			mt = message.text.replace('@','')
		else: mt = str(custom_data)
		
		if mt.isdigit():
			user = await db.fetchrow('SELECT * FROM users WHERE uid = $1', int(mt))
		else:
			user = await db.fetchrow('SELECT * FROM users WHERE username = $1', mt.lower())

		if user is None: data['message'] = await message.answer('<b>🌐 Пользователь не найден</b>',reply_markup=await kb_back('admin:menu')); return
		text = f'<b>🌐 Пользователь найден</b>\n\n<b>🃏 Профиль</b>\n<i>ID</i>:  <code>{user["uid"]}</code>\n<i>username</i>:  <code>{user["username"]}</code>\n<i>Баланс</i>:  <code>{round(user["balance"], 3)} ₽</code>\n<i>Реф. Баланс</i>:  <code>{round(user["ref_balance"], 3)} ₽</code>\n<i>Дата регистрации</i>:  <code>{datetime.strftime(datetime.fromtimestamp(user["registration_date"]),"%d.%m.%Y %H:%M")}</code>'
		
		if user['referral_from_id'] not in ['None', '', None]:
			referral_user = await db.fetchrow('SELECT * FROM users WHERE uid = $1', user['uid'])
			text += f'\n<i>Приглашён</i>:  <b><a href="tg://user?id={referral_user["uid"]}">{referral_user["username"]}</a> | <code>{referral_user["uid"]}</code></b>'
		
		if user['is_banned']:
			ban_info = await db.fetchrow('SELECT * FROM banned WHERE uid = $1', user['uid'])
			text+=f'\n\n<b>🛑✋ Блокировка</b>\n<i>Причина блокировки</i>:  <code>{ban_info["ban_reason"] if ban_info["ban_reason"] != "" else "Без причины"}</code>'
			if ban_info['unban_ts'] != 0: text+=f'\n<i>Дата разблокировки</i>:  <code>{datetime.strftime(datetime.fromtimestamp(ban_info["issue_date"]+ban_info["unban_ts"]),"%d.%m.%Y %H:%M")}</code>'

		await message.answer(text, reply_markup=await kb_admin_menu_user(user), disable_web_page_preview=True)

	await state.finish()
@dp.callback_query_handler(state=states_admin.search_user)
async def states_admin_search_user_(call: types.CallbackQuery, state: FSMContext):
	await handler_admin(call,state)


# Админ панель - Изменение баланса пользователя
@dp.message_handler(state=states_admin.change_balance)
async def states_admin_change_balance(message: types.Message, state: FSMContext):
	
	
	async with state.proxy() as data:
		try: await data['message'].delete()
		except: pass
		try: await message.delete()
		except: pass

		mt = message.text
		try: amount = float(mt)
		except: data['message'] = await message.answer('<b>Введите только число</b>'); return
		if data['is_add'] == 0: 
			await db.execute('UPDATE users SET balance = balance+$1 WHERE uid = $2', amount, data['uid'])
			try: await bot.send_message(data['uid'],f'<b>💳 Вам было выдано</b> <code>{round(amount, 3)} ₽</code>')
			except: pass
		elif data['is_add'] == 1: await db.execute('UPDATE users SET balance = balance-$1 WHERE uid = $2', amount, data['uid'])
		else: await db.execute('UPDATE users SET balance = $1 WHERE uid = $2', amount, data['uid'])
		

		return await states_admin_search_user(message, state, data['uid'])
@dp.callback_query_handler(state=states_admin.change_balance)
async def states_admin_change_balance_(call: types.CallbackQuery, state: FSMContext):
	cd = call.data

	if 'admin:menu' in cd:
		async with state.proxy() as data:
			ia = data['is_add']
			uid = data['uid']
			balance = data['balance']
			b=ia+1 if ia <= 1 else 0
			v={0:'✅ Добавить баланс ✅',1:'🔴 Минусовать баланс 🔴',2:'🟡 Установить новый баланс 🟡'}
			data['is_add'] = b

			data['m'] = await call.message.edit_text(f'<b>Введите новый баланс пользователя\n\nТекущий баланс: <code>{(round(balance, 3))} ₽</code></b>{" "*random.randint(1,9)}',reply_markup=await kb_construct(InlineKeyboardMarkup(row_width=1),{v[b]:f'cd^admin:menu:{b}:{balance}','↪ Назад':f'cd^temp:finduser:{uid}'}))
	
	else: await handler_temp(call, state)


# Админ панель - Блокировка пользователя - Причина
@dp.message_handler(state=states_admin.ban_reason_set)
async def states_admin_ban_reason_set(message: types.Message, state: FSMContext):
	ts = int(time.time())

	async with state.proxy() as data:
		user_uid = data['uid']
		try:
			await message.delete()
			await data['message'].delete()
		except: pass
		ban_reason = message.text

		try:await bot.send_message(data['uid'], f'<b>Вы были добавлены в черный список данного бота\nПричина:</b> <code>{ban_reason}</code>\n<b>Если вы считаете, что произошла ошибка - свяжитесь с <i>администратором</i> {username_support}</b>')
		except:pass
		await ban_user(user_uid, ban_reason)

		await states_admin.ban_time_set.set()
		data['message'] = await message.answer(f'<b>Пользователь заблокирован</b>\n<i>Причина блокировки:</i> <code>{ban_reason}</code>\n\nВведите <b>время через которое разблокировать пользователя</b> в <i>секундах</i>', reply_markup=await kb_construct(InlineKeyboardMarkup(row_width=2), {'1 час':f'cd^admin:menu:3600','24 часа':f'cd^admin:menu:86400','💨 Пропустить':f'cd^temp:finduser:{user_uid}'}))
@dp.callback_query_handler(state=states_admin.ban_reason_set)
async def states_admin_ban_reason_set_(call: types.CallbackQuery, state: FSMContext):
	cd = call.data.split(':')
	if 'admin' not in cd: return await handler_temp(call, state)

	ts = int(time.time())

	async with state.proxy() as data:
		try:await bot.send_message(data['uid'], f'<b>Вы были добавлены в черный список данного бота</b>\n<b>Если вы считаете, что произошла ошибка - свяжитесь с <i>администратором</i> {username_support}</b>')
		except:pass

		user_uid = data['uid']
		ban_reason = 'Нет'
		await ban_user(user_uid)

		await states_admin.ban_time_set.set()

		data['message'] = await call.message.edit_text(f'<b>Пользователь заблокирован</b>\n<i>Причина блокировки:</i> <code>{ban_reason}</code>\n\nВведите <b>время через которое разблокировать пользователя</b> в <i>секундах</i>', reply_markup=await kb_construct(InlineKeyboardMarkup(row_width=2), {'1 час':f'cd^admin:menu:3600','24 часа':f'cd^admin:menu:86400','💨 Пропустить':f'cd^temp:finduser:{user_uid}'}))

# Админ панель - Блокировка пользователя - Время разблокировки
@dp.message_handler(state=states_admin.ban_time_set)
async def states_admin_ban_time_set(message: types.Message, state: FSMContext):
	mt = message.text
	async with state.proxy() as data:
		try: await message.delete()
		except: pass
		if 'temp' in data: await data['temp'].delete()
		if mt.isdigit() is False:
			data['temp'] = await message.answer('<b>Введите только число</b>', reply_markup=await kb_close())
			return

		ban_time = int(mt)
		try: await data['message'].delete()
		except: pass

		await db.execute('UPDATE banned Set unban_ts = $1 WHERE uid = $2', ban_time, data['uid'])
		return await states_admin_search_user(message, state, data['uid'])
@dp.callback_query_handler(state=states_admin.ban_time_set)
async def states_admin_ban_time_set_(call: types.CallbackQuery, state: FSMContext):
	cd = call.data.split(':')
	async with state.proxy() as data:
		if 'temp' in data: await data['temp'].delete()

		ban_time = int(cd[2])
		if ban_time != data['uid']:
			await db.execute('UPDATE banned Set unban_ts = $1 WHERE uid = $2', ban_time, data['uid'])

		return await handler_temp(call, state, f'temp:finduser:{data["uid"]}')


# Админ панель - Рассылка - Добавление текста
@dp.message_handler(state=states_admin.spam_create_session, content_types=['photo','text'])
async def states_admin_spam_create_session(message: types.Message, state: FSMContext):
	mt = message.text
	async with state.proxy() as data: 
		try: await data['message'].delete()
		except: pass
		try: await message.delete()
		except: pass
		if data['spam_type'] == 'image':
			data['message'] = await message.answer(
				'<i>🏞 Отправьте изображение для рассылки</i>',
				reply_markup=await kb_back('admin:menu')
			)

			await states_admin.spam_add_media.set()

		elif data['spam_type'] == 'text':
			data['message'] = await message.answer(mt)
			await message.answer(
				'<i>📬 Запустить рассылку?</i>',
				reply_markup=await kb_construct(InlineKeyboardMarkup(row_width=2),
					{
						'Запустить':'cd^admin:menu:yes',
						'Нет':'cd^admin:menu',
						'↪ Назад':'cd^admin:menu'
					}
				)
			)

			await states_admin.spam_confirm.set()
		
		data['spam_text'] = mt
		data['spam_photo'] = 'None'
@dp.callback_query_handler(state=states_admin.spam_create_session)
async def states_admin_spam_create_session_(call: types.CallbackQuery, state: FSMContext):
	return await handler_admin(call, state)

# Админ панель - Рассылка - Добавление медиа
@dp.message_handler(state=states_admin.spam_add_media, content_types=['photo'])
async def states_admin_spam_add_media(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		try: await data['message'].delete()
		except: pass

		name = random.randint(1,99999)

		await message.photo[-1].download(f'{name}.jpg')
		data['message'] = await message.answer_photo(open(f'{name}.jpg', 'rb'), caption=data['spam_text'])
		
		await message.answer('<i>📬 Запустить рассылку?</i>',reply_markup=await kb_construct(InlineKeyboardMarkup(row_width=2),{'Запустить':'cd^admin:menu:yes','Нет':'cd^admin:menu','↪ Назад':'cd^admin:menu'}))
		await message.delete()
		
		data['spam_photo'] = name
		await states_admin.spam_confirm.set()
@dp.callback_query_handler(state=states_admin.spam_add_media)
async def states_admin_spam_add_media_(call: types.CallbackQuery, state: FSMContext):
	return await handler_admin(call, state)

# Админ панель - Рассылка - Подтверждение
@dp.callback_query_handler(state=states_admin.spam_confirm)
async def states_admin_spam_confirm_(call: types.CallbackQuery, state: FSMContext):
	async with state.proxy() as data:
		spam_type, spam_text, spam_photo = data['spam_type'], data['spam_text'], data['spam_photo']
		try:await data['message'].delete()
		except:pass
	
	await state.finish()
	if 'yes' in call.data:
		await call.answer('🚀 Рассылка запущена!', show_alert=True)
		asyncio.get_event_loop().create_task(users_spam(call.from_user.id, spam_type, spam_text, None if spam_photo == 'None' else spam_photo))

	return await handler_admin(call, state)


# Создание промокода
@dp.message_handler(state=states_admin.create_promocode)
async def states_admin_create_promocode(message: types.Message, state: FSMContext):
	mt = message.text
	state_data = await state.get_data()

	await delmsg(state_data['msg'], message)
	if state_data['state'] == 'reward':
		try: reward = float(mt.replace(',', '.'))
		except:
			msg = await message.answer(f'<b>Создание промокода</b>\n┗ Тип промокода:  <code>{promocode_types[state_data["promocode_type"]]}</code>\n\n<b>❌ Вознаграждение должно быть числом! Попробуйте еще раз.</b>' if state_data['promocode_type'] == 1 else f'<b>Создание промокода</b>\n┗ Тип промокода:  <code>{promocode_types[state_data["promocode_type"]]}</code>\n\n<b>Скидка должна быть числом! Попробуйте еще раз.</b>', reply_markup=await kb_admin_promocode_create(state_data['state']))
			return await state.update_data(msg=msg)

		msg = await message.answer(f'<b>Создание промокода</b>\n┣ Тип промокода:  <code>{promocode_types[state_data["promocode_type"]]}</code>\n┗ Вознаграждение:  <code>{reward}</code>\n\n<b>Отправьте количество создаваемых промокодов</b>' if state_data['promocode_type'] == 1 else f'<b>Создание промокода</b>\n┣ Тип промокода:  <code>{promocode_types[state_data["promocode_type"]]}</code>\n┗ Скидка:  <code>{reward}</code>\n\n<b>Отправьте количество использований</b>', reply_markup=await kb_admin_promocode_create('uses_amount'))
		await state.update_data(msg=msg, reward=reward, state='uses_amount')
		state_data = await state.get_data()


	elif state_data['state'] == 'uses_amount':
		if not mt.isnumeric():
			msg = await message.answer(f'<b>Создание промокода</b>\n┣ Тип промокода:  <code>{promocode_types[state_data["promocode_type"]]}</code>\n┗ Вознаграждение:  <code>{state_data["reward"]}</code>\n\n<b>❌ Кол-во промокодов должно быть целым числом! Попробуйте еще раз.</b>' if state_data['promocode_type'] == 1 else f'<b>Создание промокода</b>\n┣ Тип промокода:  <code>{promocode_types[state_data["promocode_type"]]}</code>\n┗ Скидка:  <code>{state_data["reward"]}</code>\n\n<b>❌ Кол-во использований должно быть целым числом! Попробуйте еще раз.</b>', reply_markup=await kb_admin_promocode_create(state_data['state']))
			return await state.update_data(msg=msg)
		
		await state.update_data(uses_amount=int(mt))
		state_data = await state.get_data()

		await state.finish()

		
		

		promocodes = []
		promocodes_pm = []
		if state_data['promocode_type'] == 1:
			for x in range(state_data['uses_amount']):
				promocode_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
				promocodes.append(promocode_id)
				promocodes_pm.append(f'<code>{promocode_id}</code>')
				await db.execute('INSERT INTO promocodes (promocode_id, promocode_maxuses, promocode_reward, promocode_type, promocode_activated_uids) VALUES ($1, $2, $3, $4, $5)', promocode_id, 1, state_data['reward'], state_data['promocode_type'], '')
		elif state_data['promocode_type'] == 2:
			promocode_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
			promocodes.append(promocode_id)
			promocodes_pm.append(f'<code>{promocode_id}</code>')
			await db.execute('INSERT INTO promocodes (promocode_id, promocode_maxuses, promocode_reward, promocode_type, promocode_activated_uids) VALUES ($1, $2, $3, $4, $5)', promocode_id, state_data['uses_amount'], state_data['reward'], state_data['promocode_type'], '')
		

		if len(promocodes) < 10:
			t = "\n".join(promocodes_pm)
			msg = await message.answer(f'<b>Промокоды созданы</b>\n┣ Тип промокода:  <code>{promocode_types[state_data["promocode_type"]]}</code>\n┣ Вознаграждение:  <code>{state_data["reward"]}</code>\n┗ Кол-во промокодов:  <code>{state_data["uses_amount"]}</code>\n\n{t}' if state_data['promocode_type'] == 1 else f'<b>Промокоды созданы</b>\n┣ Тип промокода:  <code>{promocode_types[state_data["promocode_type"]]}</code>\n┣ Вознаграждение:  <code>{state_data["reward"]}</code>\n┗ Кол-во использований:  <code>{state_data["uses_amount"]}</code>\n\n{t}', reply_markup=await kb_back('admin:promocode'))
		else:
			f_name = f'Sub promocodes #{random.randint(111,999)}.txt'
			open(f_name,'w',encoding='utf-8').write("\n".join(promocodes))
			await message.answer_document(open(f_name,'rb'), caption=f'<b>Промокоды созданы</b>\n┣ Тип промокода:  <code>{promocode_types[state_data["promocode_type"]]}</code>\n┣ Вознаграждение:  <code>{state_data["reward"]}</code>\n┗ Кол-во промокодов:  <code>{state_data["uses_amount"]}</code>' if state_data['promocode_type'] == 1 else f'<b>Промокоды созданы</b>\n┣ Тип промокода:  <code>{promocode_types[state_data["promocode_type"]]}</code>\n┣ Вознаграждение:  <code>{state_data["reward"]}</code>\n┗ Кол-во использований:  <code>{state_data["uses_amount"]}</code>', reply_markup=await kb_back('admin:promocode'))
			threading.Thread(target=os_delete,args=[f_name]).start()

@dp.callback_query_handler(state=states_admin.create_promocode)
async def states_admin_create_promocode_(call: types.CallbackQuery, state: FSMContext):
	cd = call.data.split(':')
	state_data = await state.get_data()

	if call.data in ('admin:menu', 'admin:promocode', 'admin:promocode:c'): return await handler_admin(call, state)
	elif state_data['state'] == 'reward':
		msg = await call.message.edit_text(f'<b>Создание промокода</b>\n┣ Тип промокода:  <code>{promocode_types[state_data["promocode_type"]]}</code>\n┗ Вознаграждение:  <code>{float(cd[4])}</code>\n\n<b>Отправьте количество создаваемых промокодов</b>' if state_data['promocode_type'] == 1 else f'<b>Создание промокода</b>\n┣ Тип промокода:  <code>{promocode_types[state_data["promocode_type"]]}</code>\n┗ Скидка:  <code>{float(cd[4])}</code>\n\n<b>Отправьте количество использований</b>', reply_markup=await kb_admin_promocode_create('uses_amount'))
		await state.update_data(msg=msg, reward=float(cd[4]), state='uses_amount')

	elif state_data['state'] == 'uses_amount':
		await state.update_data(uses_amount=int(cd[5]))
		state_data = await state.get_data()
		await state.finish()

		
		

		promocodes = []
		promocodes_pm = []
		if state_data['promocode_type'] == 1:
			for x in range(state_data['uses_amount']):
				promocode_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
				promocodes.append(promocode_id)
				promocodes_pm.append(f'<code>{promocode_id}</code>')
				await db.execute('INSERT INTO promocodes (promocode_id, promocode_maxuses, promocode_reward, promocode_type, promocode_activated_uids) VALUES ($1, $2, $3, $4, $5)', promocode_id, 1, state_data['reward'], state_data['promocode_type'], '')
		elif state_data['promocode_type'] == 2:
			promocode_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
			promocodes.append(promocode_id)
			promocodes_pm.append(f'<code>{promocode_id}</code>')
			await db.execute('INSERT INTO promocodes (promocode_id, promocode_maxuses, promocode_reward, promocode_type, promocode_activated_uids) VALUES ($1, $2, $3, $4, $5)', promocode_id, state_data['uses_amount'], state_data['reward'], state_data['promocode_type'], '')
		

		if len(promocodes) < 10:
			t = "\n".join(promocodes_pm)
			msg = await call.message.edit_text(f'<b>Промокоды созданы</b>\n┣ Тип промокода:  <code>{promocode_types[state_data["promocode_type"]]}</code>\n┣ Вознаграждение:  <code>{state_data["reward"]}</code>\n┗ Кол-во промокодов:  <code>{state_data["uses_amount"]}</code>\n\n{t}' if state_data['promocode_type'] == 1 else f'<b>Промокоды созданы</b>\n┣ Тип промокода:  <code>{promocode_types[state_data["promocode_type"]]}</code>\n┣ Вознаграждение:  <code>{state_data["reward"]}</code>\n┗ Кол-во использований:  <code>{state_data["uses_amount"]}</code>\n\n{t}', reply_markup=await kb_back('admin:promocode'))
		else:
			f_name = f'Sub promocodes #{random.randint(111,999)}.txt'
			open(f_name,'w',encoding='utf-8').write("\n".join(promocodes))
			await call.message.answer_document(open(f_name,'rb'), caption=f'<b>Промокоды созданы</b>\n┣ Тип промокода:  <code>{promocode_types[state_data["promocode_type"]]}</code>\n┣ Вознаграждение:  <code>{state_data["reward"]}</code>\n┗ Кол-во промокодов:  <code>{state_data["uses_amount"]}</code>' if state_data['promocode_type'] == 1 else f'<b>Промокоды созданы</b>\n┣ Тип промокода:  <code>{promocode_types[state_data["promocode_type"]]}</code>\n┣ Вознаграждение:  <code>{state_data["reward"]}</code>\n┗ Кол-во использований:  <code>{state_data["uses_amount"]}</code>', reply_markup=await kb_back('admin:promocode'))
			threading.Thread(target=os_delete,args=[f_name]).start()


async def ban_user(user_uid: int, ban_reason = ''):
	ts = int(time.time())
	async with db.pool.acquire() as conn:
		await conn.execute('INSERT INTO banned (uid, issue_date, ban_reason) VALUES ($1, $2, $3)', user_uid, ts, ban_reason)
		await conn.execute('UPDATE users Set is_banned = True WHERE uid = $1', user_uid)
	
#################################################################################################################################
async def on_startup(dp):
	await db.init_pool()

	global bot_info
	bot_info=await bot.get_me()

	for x in range(10):
		try: await ssf_client.get_services(True) # Обновление данных о текущих сервисах
		except:
			await asyncio.sleep(2)
			continue
		break


	async def set_default_commands(dp):
		await dp.bot.set_my_commands([types.BotCommand("start", "Запустить бота")])
	await set_default_commands(dp)

	asyncio.get_event_loop().create_task(runTasks())

if __name__ == '__main__':
	dp.middleware.setup(ThrottlingMiddleware())

	try: executor.start_polling(dp, on_startup=on_startup)
	except Exception as error: logging.critical('Неверный токен бота!')