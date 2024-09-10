import json

from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from cashews import cache

from functions import *
from config import *
from loader import db
from services_api import *

#################################################################################################################################
async def kb_construct(keyboard = None, q = {}, row_width = 2):
	if not keyboard: keyboard = InlineKeyboardMarkup(row_width)
	if type(q) is dict:
		for x in q:
			_ = q[x].split('^')
			if _[0] == 'url': keyboard.insert(InlineKeyboardButton(x,url=_[1]))

			elif _[0] == 'cd': keyboard.insert(InlineKeyboardButton(x,callback_data=_[1]))
	else:
		for x in q: keyboard.insert(x)

	return keyboard
#################################################################################################################################
cache.setup("mem://")

async def kb_channels(uid, channels):
	s = {channels_data[x]['title']: f'url^{channels_data[x]["invite_link"]}' for x in channels}
	keyboard = await kb_construct(InlineKeyboardMarkup(row_width=1), s)
	keyboard.add(InlineKeyboardButton('✨ Проверить подписку', callback_data='utils:check_sub'))
	return keyboard


### USER ###
async def kb_menu(uid):
	keyboard = ReplyKeyboardMarkup(resize_keyboard=True,row_width=2)
	s = ['⭐️ Заказать бусты', '', '💰 Профиль|Баланс', 'ℹ️ Информация']
	if uid in admin_ids: s.append('🧑🏻‍💻 Админ меню')
	for x in s: keyboard.insert(x)
	return keyboard

async def kb_profile(user_db):
	s = {'💰 Пополнить баланс':'cd^user:refill_balance:0', '🎟 Активировать купон':'cd^user:activate_promocode', '👨‍👩‍👧‍👦 Реферальная система':'cd^user:referal_program', '🛒 Мои заказы':'cd^user:show_orders'}

	keyboard = await kb_construct(InlineKeyboardMarkup(row_width=2), s)
	keyboard.add(InlineKeyboardButton('❌ Закрыть',callback_data='utils:delete'))
	return keyboard

async def kb_ref_menu():
	s = {'💸 Запросить вывод': 'cd^user:request_ref_withdraw'}

	keyboard = await kb_construct(InlineKeyboardMarkup(row_width=1), s)
	keyboard.add(InlineKeyboardButton('↪ Назад', callback_data='user:menu'))
	return keyboard

async def kb_faq(i=0):
	s = {f'{"❓" if i == x else "❔"} {faq_text_ids[x]}':f'cd^utils:faq:{i}:{x}' for x in faq_text_ids}

	keyboard = await kb_construct(InlineKeyboardMarkup(row_width=1), s)
	keyboard.add(InlineKeyboardButton('❌ Закрыть',callback_data='utils:delete'))
	return keyboard

async def kb_about():
	s = {'⚙️ Техническая поддержка':f'url^{url_support}', '🔗 Все проекты':f'url^{url_our_projects}', '📖 Правила':f'url^{url_rules}'}

	keyboard = await kb_construct(InlineKeyboardMarkup(row_width=2), s)
	keyboard.add(InlineKeyboardButton('❌ Закрыть',callback_data='utils:delete'))
	return keyboard

async def kb_user_orders(orders, uid = None):
	if uid: s = {f"{x['order_category_name']} — {x['order_service_name']} | {x['order_id']}": f'cd^admin:orders:{uid}:{x["id"]}' for x in orders}
	else: s = {f"{x['order_category_name']} — {x['order_service_name']} | {x['order_id']}": f'cd^user:show_order:{x["id"]}' for x in orders}
	
	keyboard = await kb_construct(InlineKeyboardMarkup(row_width=1), s)
	keyboard.add(InlineKeyboardButton('↪ Назад', callback_data=f'temp:finduser:{uid}' if uid else 'user:menu'))
	return keyboard

async def kb_user_order(uid = None):
	s = {}

	keyboard = await kb_construct(InlineKeyboardMarkup(row_width=2), s)
	keyboard.add(InlineKeyboardButton('↪ Назад',callback_data=f'admin:orders:{uid}' if uid else 'user:show_orders'))
	return keyboard



### ADMIN ###
async def kb_admin_menu():
	s = {'📢 Рассылка':'cd^admin:spam_create', '🔍 Поиск профиля':'cd^admin:search_user', '🚫 В бане':'cd^admin:all_banned', '🧾 Промокоды': 'cd^admin:promocode', '📰 Информация о боте':'cd^admin:stats'}#'📃 Поиск чеков':'cd^admin:find_receipt', 
	keyboard = await kb_construct(InlineKeyboardMarkup(row_width=2), s)
	keyboard.add(InlineKeyboardButton('❌ Закрыть',callback_data='utils:delete'))
	return keyboard

async def kb_spam():
	s = {'🖼 Текст + картинка':'cd^admin:spam_create:image','📜 Текст':'cd^admin:spam_create:text'}

	keyboard = await kb_construct(InlineKeyboardMarkup(row_width=2),s)
	keyboard.add(InlineKeyboardButton('↪ Назад',callback_data='admin:menu'))
	return keyboard

async def kb_admin_menu_user(user):
	uid = user['uid']
	s = {'Изменить баланс': f'cd^admin:change_balance:{uid}', ('Разблокировать' if user["is_banned"] else 'Заблокировать'): f'cd^admin:ban:{0 if user["is_banned"] else 1}:{uid}', 'Список заказов': f'cd^admin:orders:{uid}'}

	keyboard = await kb_construct(InlineKeyboardMarkup(row_width=2),s)
	keyboard.add(InlineKeyboardButton('↪ Назад',callback_data='admin:menu'))
	return keyboard

async def kb_admin_banned_users():
	s = {}
	for x in await db.fetch('SELECT * FROM users WHERE is_banned = True'):
		s[x['uid'] if x['username'] in [None,'none'] else x['username']] = f'cd^admin:find_user_:{x["uid"]}'

	keyboard = await kb_construct(InlineKeyboardMarkup(row_width=2),s)
	keyboard.add(InlineKeyboardButton('↪ Назад',callback_data=f'admin:menu'))

	return keyboard

async def kb_admin_promocode():
	s = {'Создать промокод': 'cd^admin:promocode:c', 'Получить промокоды': 'cd^admin:promocode:g'}

	keyboard = await kb_construct(InlineKeyboardMarkup(row_width=2), s)
	keyboard.add(InlineKeyboardButton('↪ Назад', callback_data=f'admin:menu'))

	return keyboard

async def kb_admin_promocode_create(state, promocode_type = 1, reward = 1):
	if state == 'type':
		s = {'Деньги на баланс': 'cd^admin:promocode:c:1', 'Скидка в %': 'cd^admin:promocode:c:2'}
		back_b = InlineKeyboardButton('↪ Назад', callback_data=f'admin:promocode')
	
	elif state == 'reward':		
		s = {1: f'cd^admin:promocode:r:{promocode_type}:1', 5: f'cd^admin:promocode:r:{promocode_type}:5', 10: f'cd^admin:promocode:r:{promocode_type}:10', 100: f'cd^admin:promocode:r:{promocode_type}:100'}
		back_b = InlineKeyboardButton('↪ Назад', callback_data=f'admin:promocode:c')

	elif state == 'uses_amount':		
		s = {1: f'cd^admin:promocode:r:{promocode_type}:{reward}:1', 5: f'cd^admin:promocode:r:{promocode_type}:{reward}:5', 10: f'cd^admin:promocode:r:{promocode_type}:{reward}:10', 20: f'cd^admin:promocode:r:{promocode_type}:{reward}:20', 100: f'cd^admin:promocode:r:{promocode_type}:{reward}:100'}
		back_b = InlineKeyboardButton('↪ Назад', callback_data=f'admin:promocode:c')


	keyboard = await kb_construct(InlineKeyboardMarkup(row_width=2), s)
	keyboard.add(back_b)

	return keyboard

### SMM ###
@cache(ttl='6h')
async def kb_get_categories(category_name = None, category_type_hash = None, page = 1, prefix = None):
	if prefix in ('', 'None'): prefix = None
	page = int(page)
	keyboard = InlineKeyboardMarkup(row_width=2)

	if category_name and category_type_hash:
		cpl = epp['service']
		if len(sets_accepted_services) == 0: _s = sorted([x for x in (await ssf_client.decode(category_type_hash=category_type_hash)).values() if int(x['service_id']) not in sets_banned_services], key=lambda x: x['price'])
		else: _s = sorted([x for x in (await ssf_client.decode(category_type_hash=category_type_hash)).values() if int(x['service_id']) in sets_accepted_services], key=lambda x: x['price'])
		s = {x['name']: f'smm:cs:{category_name}:{category_type_hash}:{x["service_id"]}:1' for x in _s[page*cpl-cpl:(page+1)*cpl-cpl]}
		for x in s: keyboard.add(InlineKeyboardButton(x, callback_data=s[x]))
		s = {'': 'by_plowside'}

		if page > 1: s['❮❮'] = f'smm:ct:{category_name}:{category_type_hash}:{page-1}'
		if len(_s[page*cpl-cpl:(page+1)*cpl]) > cpl: s['❯❯'] = f'smm:ct:{category_name}:{category_type_hash}:{page+1}'
		back_b = InlineKeyboardButton('↪ Назад', callback_data=f'smm:c:{category_name}:1')

	elif category_name:
		services = await ssf_client.get_services()
		cpl = epp['category_type']
		_s = [x for x in services[rpf(category_name)]]

		s = {x: f'smm:ct:{category_name}:{(await get_hash(rpf(category_name) + "_" + x))[:10]}:1' for x in _s[page*cpl-cpl:(page+1)*cpl-cpl]}
		for x in s: keyboard.add(InlineKeyboardButton(x, callback_data=s[x]))
		s = {'': 'by_plowside'}

		if page > 1: s['❮❮'] = f'smm:c:{category_name}:{page-1}'
		if len(_s[page*cpl-cpl:(page+1)*cpl]) > cpl: s['❯❯'] = f'smm:c:{category_name}:{page+1}'
		back_b = InlineKeyboardButton('↪ Назад', callback_data=f'smm:menu:1:{prefix}')

	else:
		cpl = epp['category']
		if not prefix:
			_s = list((sets_categories[x], x) for x in sets_categories if cpf(x))
			back_b = InlineKeyboardButton('❌ Закрыть', callback_data='utils:delete')
		else:
			_s = list((sets_categories[x], x) for x in sets_categories if x.startswith(prefix) and not x.startswith('__'))
			back_b = InlineKeyboardButton('↪ Назад', callback_data='smm:menu:1')

		s = {x[0]: f'smm:c:{x[1]}:1' for x in _s[page*cpl-cpl:(page+1)*cpl-cpl] if x[0]}
		for x in s: keyboard.add(InlineKeyboardButton(x, callback_data=s[x]))
		s = {'': 'by_plowside'}

		if page > 1: s['❮❮'] = f'smm:menu:{page-1}:{prefix}'
		if len(_s[page*cpl-cpl:(page+1)*cpl]) > cpl: s['❯❯'] = f'smm:menu:{page+1}:{prefix}'


	for x in s: keyboard.insert(InlineKeyboardButton(x, callback_data=s[x]))
	keyboard.add(back_b)
	return keyboard


@cache(ttl='6h')
async def kb_get_category_types(category_name = None, category_type_hash = None, service_id = None, page = 0):
	s = {'💎 Заказать': f'cd^smm:b:{category_name}:{category_type_hash}:{service_id}:1'}
	keyboard = await kb_construct(InlineKeyboardMarkup(row_width=1), s)
	keyboard.add(InlineKeyboardButton('↪ Назад',callback_data=f'smm:ct:{category_name}:{category_type_hash}:1'))
	return keyboard



### PAYMENT ###
async def kb_payment_select(amount):
	s = {payment_services_names[x]: f'cd^user:refill_balance:2:{x}:{amount}' for x in payment_services if payment_services[x]}

	keyboard = await kb_construct(InlineKeyboardMarkup(row_width=1),s)
	keyboard.add(InlineKeyboardButton('↪ Назад',callback_data=f'user:refill_balance:0'))
	return keyboard

async def kb_refill_balancePrices(n=[200,300,500,1000,2500,5000]):
	s = {f"{x} ₽":f"cd^user:refill_balance:1:{x}" for x in n}
	keyboard = await kb_construct(InlineKeyboardMarkup(row_width=3),s)
	keyboard.add(InlineKeyboardButton('↪ Назад',callback_data='user:menu'))
	return keyboard

async def kb_payment_get(amount, url):
	s = {'🔥 Перейти к оплате':f'url^{url}','👤 Профиль':'cd^user:menu','🆘 Техническая поддержка':f'url^{url_support}'}
	keyboard = await kb_construct(InlineKeyboardMarkup(row_width=2),s)
	keyboard.add(InlineKeyboardButton('↪ Назад',callback_data=f'user:refill_balance:1:{amount}'))
	return keyboard


### UTILS ###
async def kb_close():
	keyboard = await kb_construct(InlineKeyboardMarkup(), {'❌ Закрыть':'cd^utils:delete'})

	return keyboard

async def kb_back(callback_data = 'user:menu', text = '↪ Назад'):
	keyboard = InlineKeyboardMarkup()

	keyboard.add(InlineKeyboardButton(text, callback_data=callback_data))
	return keyboard