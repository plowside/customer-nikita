import threading, traceback, asyncio, logging, hashlib, httpx, random, time, json, uuid, re, os
from cashews import cache

from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

from loader import bot, db
from config import *
from services_api import *

#################################################################################################################################
async def kb_construct(keyboard = None, query = {}, row_width = 2):
	if not keyboard: keyboard = InlineKeyboardMarkup(row_width)
	if type(query) is dict:
		for x in query:
			_ = query[x].split('^')
			if _[0] == 'url': keyboard.insert(InlineKeyboardButton(x,url=_[1]))

			elif _[0] == 'cd': keyboard.insert(InlineKeyboardButton(x,callback_data=_[1]))
	else:
		for x in query: keyboard.insert(x)

	return keyboard

async def kb_close():
	keyboard = await kb_construct(InlineKeyboardMarkup(), {'❌ Закрыть':'cd^utils:delete'})

	return keyboard
#################################################################################################################################
logging.getLogger("httpx").setLevel(logging.ERROR)
cache.setup("mem://")

# Получить информацию о пользователе из объекта types.Message | types.CallbackQuery
def get_user(data):
	return [data.from_user.id, (data.from_user.username.lower() if data.from_user.username is not None else None), data.from_user.first_name]

def format_user_url(uid = None, username = None, first_name = None, user_db = None):
	if user_db:
		uid = user_db['uid']; username = user_db['username']; first_name = user_db['first_name']
	first_name = 'without_first_name' if first_name in ('', None) else first_name
	return f'<a href="{username}.t.me">{first_name}</a>' if username else f'<a href="tg://user?id={uid}">{first_name}</a>'

# Генерация "чека"
def gen_id():
	mac_address = uuid.getnode()
	time_unix = int(str(time.time_ns())[:16])

	return str(mac_address + time_unix)


# Умное округление числа
@cache(ttl=None)
async def round_to_precision(num):
	split = 2
	for x in str(num).split('.')[1]:
		if x == '0': split += 1
		else: break
	return round(num, split)

@cache(ttl='1m', key='check_channel:{channel_id}:{uid}')
async def check_channel(channel_id, uid):
	try:
		member = await bot.get_chat_member(channel_id, uid)
		return member.status in 'member|administrator|creator'
	except: return False

# Удаление какого либо файла
def os_delete(*paths):
	for path in paths:
		for x in range(50):
			try: os.remove(path); break
			except: time.sleep(.8)


async def get_discount(uid):
	discount = await db.fetchrow('SELECT * FROM discounts WHERE (uid, discount_is_active) = ($1, True)', uid)
	return discount

# Удалить одно/несколько сообщений
async def delmsg(*messages):
	for x in messages:
		try:
			if isinstance(x, dict): await bot.delete_message(x['chat_id'], x['message_id'])
			else: await x.delete()
		except Exception as e: logging.debug(f'Ошибка при удалении сообщения: {e}')

# Отправление сообщения всем админам
async def admin_spam(text, reply_markup = None):
	for x in admin_ids:
		try: await bot.send_message(x, text, reply_markup=reply_markup if reply_markup else await kb_close(), disable_web_page_preview=True)
		except Exception as e: logging.error(f'Error on admin_spam[user_id: {x}]: {e}')

# Отправление сообщения всем пользователям
async def users_spam(fromId=None, spam_type=None, spam_text=None, spam_image=None):
	users = await db.fetch('SELECT uid FROM users')
	v, nv = 0, 0
	if spam_type == 'text':
		for x in users:
			try: await bot.send_message(x['uid'], spam_text, reply_markup=await kb_construct(InlineKeyboardMarkup(row_width=advert_button_data['row_width']), advert_button_data['buttons'])); v+=1
			except: nv+=1
	
	elif spam_type == 'image':
		for x in users:
			try: await bot.send_photo(x['uid'], open(f'{spam_image}.jpg','rb'), caption=spam_text, reply_markup=await kb_construct(InlineKeyboardMarkup(row_width=advert_button_data['row_width']), advert_button_data['buttons'])); v+=1
			except: nv+=1

	threading.Thread(target=os_delete, args=[f'{spam_image}.jpg']).start()
	await bot.send_message(fromId, f'<b>📮 Рассылка завершена!</b>\n<i>Отправлено</i>: <code>{v}</code>\n<i>Заблокировали бота</i>: <code>{nv}</code>', reply_markup=await kb_construct(InlineKeyboardMarkup(row_width=1), {'❌ Закрыть':'cd^utils:delete'}))



# Получение ссылки для пополнения баланса
async def payment_get_url(payment_service, amount, uid):
	ts = f'{uid}:{int(time.time())}:{random.randint(111,999)}'

	try:
		if payment_service == 'crystalpay':
			async with httpx.AsyncClient() as client:
				req = (await client.post('https://api.crystalpay.io/v2/invoice/create/', json={'auth_login': crystalpay_login, 'auth_secret': crystalpay_secret, 'amount': amount, 'type': 'purchase', 'description': crystalpay_description, 'extra': str(uid), 'lifetime': payment_life_time})).json()

				if req['error']: return (False, None, None)
				invoice_id = req['id']
				invoice_url = req['url']
				return (True, invoice_id, invoice_url)

		elif payment_service == 'payok':
			sign = f'{amount}|{ts}|{payok_shop}|{payok_io_currency}|{uid}|{payok_secret}'
			result = hashlib.md5(sign.encode('utf-8')).hexdigest()
			
			return (True, ts, f'https://payok.io/pay?amount={amount}&payment={ts}&shop={payok_shop}&desc={uid}&sign={result}')

		elif payment_service == 'aaio':
			sign = f':'.join([str(aaio_shop_id),str(amount),str('RUB'),str(aaio_secret_1),str(ts)])
			params = {
				'merchant_id': aaio_shop_id,
				'amount': amount,
				'currency': aaio_currency,
				'order_id': ts,
				'sign': hashlib.sha256(sign.encode('utf-8')).hexdigest(),
				'desc': aaio_description,
				'lang': 'ru'
			}
			return (True, ts, "https://aaio.so/merchant/pay?"+urlencode(params))
	except Exception as e:
		logging.error(f'[payment_get_url | LINE:{traceback.extract_tb(e.__traceback__)[-1].lineno}] Общая ошибка: {e}')
		return (False, None, None)

# Проверка статуса пополнения баланса
async def payment_check(payment_service, amount, uid, uum, uuf, invoce_id):
	ts = int(time.time())
	is_payed = False
	async with httpx.AsyncClient(timeout=120) as client:
		while True:
			await asyncio.sleep(20)
			try:
				if int(time.time()) - ts >= payment_check_time*60: break

				if payment_service == 'crystalpay':
					req = (await client.post('https://api.crystalpay.io/v2/invoice/info/', json={'auth_login': crystalpay_login, 'auth_secret': crystalpay_secret, 'id':invoce_id})).json()
					if req['state'] == 'payed':
						is_payed = True
						break

					#elif req['state'] in ['failed','wrongamount']: break


				elif payment_service == 'payok':
					req = (await client.post('https://payok.io/api/transaction', data={'API_ID': payok_api_id, 'API_KEY': payok_api, 'shop': payok_shop, 'payment': invoce_id}))
					try: req = req.json()
					except: logging.error(req); break

					if req['status'] == 'error': 
						if req['error_code'] in ['10','25']: continue
						else: 
							logging.error(req)
							continue
					if req['1']['transaction_status'] in [1,'1']:
						is_payed = True
						try: amount = float(req['1']['amount_profit'])
						except: pass
						break


				elif payment_service == 'aaio':
					req = (await client.post('https://aaio.so/api/info-pay', data={'merchant_id': aaio_shop_id, 'order_id': str(invoce_id)}, headers={'Accept': 'application/json', 'X-Api-Key': aaio_api}))
					if req.status_code == 401:
						break
					elif req.status_code in [200, 400]:
						try: req = req.json()
						except: continue
					else: continue

					if 'status' not in req: continue
					if req['status'] in ['success', 'hold']:
						is_payed = True
						break

				elif payment_service == 'telegram':
					break

			except (httpx.ReadTimeout, json.decoder.JSONDecodeError): pass
			except Exception as e: logging.error(f'PAYMENT [{payment_service} | LINE:{traceback.extract_tb(e.__traceback__)[-1].lineno}] : {type(e)} --> [{e}]')

		if is_payed:
			referral_from_id = (await db.fetchrow('SELECT referral_from_id FROM users WHERE uid = $1', uid))['referral_from_id']
			await db.execute('INSERT INTO transactions_refill(transaction_id, uid, issue_date, payment_service_name, payment_amount) VALUES ($1, $2, $3, $4, $5)', invoce_id, uid, int(time.time()), payment_service, amount)

			amount = round(amount, 2)
			if referral_from_id:
				referral_amount = round(amount*referral_percent, 2)
				db_referral_from_id = await db.fetchrow('SELECT * FROM users WHERE uid = $1', referral_from_id)
				await db.execute('UPDATE users SET ref_balance = ref_balance + $1 WHERE uid = $2', referral_amount, referral_from_id)
				
				url = f'<a href="t.me/{uum}">{uuf}</a>' if uum else f'<a href="tg://user?id={uid}">{uuf}</a>'
				try: await bot.send_message(referral_from_id, f'<b>💰 Ваш реферал {url} пополнил баланс на сумму</b> <code>{amount} ₽</code>\n<b>📃 Вы получили</b> <code>{referral_amount} ₽</code>', reply_markup=await kb_construct(InlineKeyboardMarkup(row_width=1), {'❌ Закрыть':'cd^utils:delete'}), disable_web_page_preview=True)
				except: pass
				referral_from_id_username = db_referral_from_id['username']
				url = f'<a href="t.me/{referral_from_id_username}">{referral_from_id_username}</a>' if referral_from_id_username not in ['none', None] else f'<a href="tg://user?id={referral_from_id}">{referral_from_id_username}</a>'
				await admin_spam(f'<b>💰 Пользователь {url} (<code>{referral_from_id}</code>) получил с реферала <code>{referral_amount} ₽</code></b>')

			await admin_spam(f'<b>{payment_service.capitalize()}</b>\n<i>Пользователь:</i> <b>@{uum} | <code>{uid}</code></b>\n<i>Сумма пополнения:</i> <code>{amount} ₽</code>')
			await db.execute('UPDATE users SET balance = balance + $1 WHERE uid = $2', amount, uid)
			try: await bot.send_message(uid, f'<b>🌀 Ваш баланс пополнен на сумму  <code>{amount} ₽</code></b>', reply_markup=await kb_construct(InlineKeyboardMarkup(row_width=1), {'❌ Закрыть':'cd^utils:delete'}))
			except: pass



# Проверка на разбан
async def watcher_unban():
	while True:
		async with db.pool.acquire() as conn:
			try:
				banned = await conn.fetch('SELECT uid FROM banned WHERE unban_ts != 0')
				for x in banned:
					user_id = x['uid']
					await conn.execute('UPDATE users SET is_banned = False WHERE uid = $1', user_id)
					await conn.execute('DELETE FROM banned WHERE uid = $1', user_id)
			except Exception as e:
				logging.error(f'Error on watcher_unban: {e}')
		await asyncio.sleep(60)

# Проверка на баланс панели и обновление скидок
async def watcher_balance_updater():
	last_balance = -1
	orders_refunded = []
	while True:
		try:
			async with db.pool.acquire() as conn:

				await conn.execute('UPDATE discounts SET discount_is_active = False WHERE discount_activations_counter >= discount_maxuses')
				balance = (await ssf_client.get_balance()).get('balance')
				balance = float(balance) if balance else balance
				if balance != None and balance < alert_min_balance and last_balance != balance:
					last_balance = balance
					await admin_spam(f'<b>❗️ Баланс панели ниже установленного лимита  (<code>{alert_min_balance} ₽</code>) ❗️\n\nБаланс панели: <code>{balance} ₽</code></b>')

				'''
				Статусы заказа
				0 - без статуса
				1 - всё отлично, заказ выполнен
				2 - отменён, деньги возвращены
				'''
				orders = await conn.fetch('SELECT * FROM orders WHERE order_status = 0')
				if len(orders) > 0:
					orders_id = [str(x['order_id']) for x in orders]
					orders_dict = {x['order_id']: x for x in orders}


					try: orders_status = await ssf_client.get_orders(orders_id)
					except:
						logging.error(f'[watcher_balance_updater] Не удалось получить заказы: {orders_status}')

					for x in orders_status:
						try:
							order = orders_status[x]
							order_id = int(x)
							order_db = orders_dict[order_id]
							if order_id in orders_refunded:
								continue

							if order['status'] in ['Completed']:
								await conn.execute('UPDATE orders SET order_status = 1 WHERE order_id = $1', order_id)
							elif order['status'] in ['Closed', 'Canceled', 'Partial']:
								orders_refunded.append(order_id)
								user_db = await conn.fetchrow('SELECT * FROM users WHERE uid = $1', order_db['uid'])
								await admin_spam(f'<b>🌀 Возврат средств</b>\n├ Пользователь: {format_user_url(user_db=user_db)}|<code>{user_db["uid"]}</code>\n├ ID Заказа:  <code>{order_id}</code>\n└ Сумма возврата:  <code>{order_db["order_price"]} ₽</code>', reply_markup=await kb_construct(InlineKeyboardMarkup(row_width=2), {'✅ Разрешить': f'cd^admin:refund:{order_id}:accept', '❌ Отклонить': f'cd^admin:refund:{order_id}:decline', '✍️ Своя сумма': f'cd^admin:refund:{order_id}:custom'}))
						except KeyError:
							pass
						except Exception as e:
							logging.error(f'[watcher_balance_updater | LINE:{traceback.extract_tb(e.__traceback__)[-1].lineno}] Ошибка проверки статуса заказа [order_id: {x}]: {e}')
		except Exception as e:
			logging.error(f'[watcher_balance_updater | LINE:{traceback.extract_tb(e.__traceback__)[-1].lineno}] Общая ошибка: {e}')
			
		await asyncio.sleep(300)

# Запуск задач при запуске бота
async def runTasks():
	asyncio.get_event_loop().create_task(watcher_unban()) # Заблокированные пользователи
	asyncio.get_event_loop().create_task(watcher_balance_updater()) # Баланс панели и скидки
	for channel in channels_to_check:
		try:
			chat = await bot.get_chat(chat_id=channel['id'])
			channels_data[chat['id']] = {'invite_link': channel['url'], 'title': channel['title']}
		except Exception as e: logging.error(f'Не удалось получить ссылку на канал [{channel["id"]}]: {e}')


# Получить данные о рефералах
#@cache(ttl="1m")
async def get_ref_stats(uid):
	ref_len = (await db.fetchrow('SELECT COUNT(id) AS q FROM users WHERE referral_from_id = $1', uid))['q']
	ref_profit = round((await db.fetchrow('SELECT COALESCE(SUM(payment_amount * $1), 0) AS q FROM transactions_refill WHERE uid IN (SELECT uid FROM users WHERE referral_from_id = $2)', referral_percent, uid))['q'], 2)
	ref_balance = round((await db.fetchrow('SELECT * FROM users WHERE uid = $1', uid))['ref_balance'], 1)

	return ref_len, ref_profit, ref_balance


async def smm_create_task(uid: int, task_data: dict):
	user_db = await db.fetchrow('SELECT * FROM users WHERE uid = $1', uid)
	if task_data['price'] > 0 and user_db['balance'] < task_data['price']:
		return {'status': False, 'msg': 'Недостаточно средств на балансе'}

	order_data = None
	try:
		unix = int(time.time())
		order_data = await ssf_client.create_order(service_id=task_data['service_id'], amount=task_data['amount'], url=task_data['url'])
		if 'error' in order_data:
			if order_data.get('error') == 'neworder.error.not_enough_funds':
				await admin_spam(f'<b>❗️❗️ Недостаточно средств на балансе панели ❗️❗️</b>\n\nЗаказ на <code>{task_data["price"]}₽</code>', await kb_construct(InlineKeyboardMarkup(row_width=1), {'Уведомить пользователя о пополнении': f'cd^utils:dm_user:{uid}:panel_balance_up', '❌ Закрыть':'cd^utils:delete'}))
			order_data['message'] = errors_text.get(order_data.get('error'))
			if not order_data['message']:
				order_data['message'] = 'Неизвестная ошибка, попробуйте позже'
				await admin_spam(f'<b>❗️❗️ Неизвестная ошибка: <code>{order_data.get("error")}</code>❗️❗️</b>', await kb_construct(InlineKeyboardMarkup(row_width=1), {'Уведомить пользователя о пополнении': f'cd^utils:dm_user:{uid}:panel_balance_up', '❌ Закрыть':'cd^utils:delete'}))

			return {'status': False, 'msg': order_data['message']}
		if 'order' not in order_data:
			logging.error(f'Не получил order_id: {order_data}')
			return {'status': False, 'msg': 'Не удалось создать заказ.'}
		order_id = order_data['order']

		order_service_name = ssf_client.all_data['category_type_hash'].get(f'{rpf(task_data["category_name"])}_{task_data["category_type_hash"]}')
		await admin_spam(f'<b>ℹ️ Новый заказ\n┣ 👁‍🗨 ID заказа:  <code>{order_id}</code>\n┣ 💈 Категория:  <code>{sets_categories[task_data["category_name"]]}</code>\n┣ ⭐️ Услуга:  <code>{order_service_name}</code>\n┣ 🆔 Пользователь:  {format_user_url(user_db=user_db)} (<code>{uid}</code>)\n┣ 🚀 Количество:  <code>{task_data["amount"]} шт.</code>\n┗ 💰 Цена:  <code>{task_data["price"]} ₽</code></b>')

		discount = await get_discount(uid)
		if discount:
			await db.execute('UPDATE discounts SET (discount_activations_counter, discount_is_active) = (discount_activations_counter + 1, $1) WHERE id = $2', not (discount['discount_activations_counter'] + 1 >= discount['discount_maxuses']), discount['id'])

		if task_data['price'] > 0:
			await db.execute('UPDATE users SET balance = balance - $1 WHERE uid = $2', task_data['price'], uid)
		await db.execute('INSERT INTO orders(uid, order_id, order_url, order_orig_price, order_orig_price_per_one, order_price, order_price_per_one, order_amount, order_category_name, order_service_name, order_service_id, unix) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)', uid, order_id, task_data['url'], task_data['orig_price'], task_data['orig_price_per_one'], task_data['price'], task_data['price_per_one'], task_data['amount'], sets_categories[task_data['category_name']], order_service_name, task_data['service_id'], unix)

		order_id = (await db.fetchrow('SELECT * FROM orders WHERE (uid, order_id, unix) = ($1, $2, $3)', uid, order_id, unix))['id']
		return {'status': True, 'order_id': order_id}
	except Exception as e:
		await db.execute('UPDATE users SET balance = balance - $1 WHERE uid = $2', task_data['price'], uid)
		
		if order_data: logging.info('create_order', order_data)
		logging.error(f'[smm_create_task | LINE:{traceback.extract_tb(e.__traceback__)[-1].lineno}] Общая ошибка:\n{traceback.format_exc()}')
		return {'status': False, 'msg': 'Неизвестная ошибка при создании операции, напишите в поддержку.'}


############################## ФОРМАТИРОВАНИЕ ТЕКСТА|ДАННЫХ ##############################
def timeFormat(time):
	if time <= 7200:
		time = int(time/60)
		return (time, morpher(time, 'минут'))
	elif time <= 86400: return (time/3600, morpher(int(time/3600), 'часов'))
	else: 
		return (time/86400, morpher(int(time/86400), 'дней'))

def r_format(_):
	return '{:,}'.format(_)

def morpher(num, presset = 'час', cases = None):
	pressets = {
		'днейднядень': {'nom': 'день', 'gen': 'дня', 'plu': 'дней'},
		'часовчасычас': {'nom': 'час', 'gen': 'часа', 'plu': 'часов'},
		'минутминутыминута': {'nom': 'минута', 'gen': 'минуты', 'plu': 'минут'},
		'секундсекундысекунда': {'nom': 'секунда', 'gen': 'секунды', 'plu': 'секунд'},
		'сервисовсервисасервис': {'nom': 'сервис', 'gen': 'сервиса', 'plu': 'сервисов'},
		'рублейрублярубль': {'nom': 'рубль', 'gen': 'рубля', 'plu': 'рублей'},
		'задачзадачизадача': {'nom': 'задача', 'gen': 'задачи', 'plu': 'задач'},
		'номеровномераномер': {'nom': 'номер', 'gen': 'номера', 'plu': 'номеров'}
	}
	if cases == None:
		cases = [pressets[x] for x in pressets if presset in x][0]

	z = {0:'nom', 1:'gen', 2:'plu'}
	if type(cases) is not dict:
		cases_ = cases
		cases = {}
		for i, x in enumerate(cases_):
			cases[z[i]] = x
	num = abs(num)
	word = ''
	if '.' in str(num):
		word = cases['gen']
	else:
		last_two_digits = num % 100
		last_digit = num % 10

		if (last_digit >= 2 and last_digit <= 4 and last_two_digits >= 20):
			word = cases['gen']
		elif (last_digit >= 2 and last_digit <= 4 and last_two_digits <= 10):
			word = cases['gen']
		elif (last_digit == 1 and last_two_digits != 11) or (last_digit >= 2 and last_digit <= 4 and (last_two_digits < 10 or last_two_digits >= 20)):
			word = cases['nom']
		else:
			word = cases['plu']

	return word