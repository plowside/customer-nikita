from telethon.tl.types import *

############################## PATH SETTINGS #############################
path_sessions = 'data/сессии' # Путь до сессий
path_avatars = 'data/аватарки' # Путь до аватарок
path_names = 'data/имена.txt' # Путь до имён
path_surnames = 'data/фамилии.txt' # Путь до фамилий
path_bio = 'data/Обо мне.txt' # Путь до био
path_chatlists = 'data/Ссылки на чатлисты.txt' # Путь до чатлистов


proxy = '151.236.25.239:12806:modeler_1MZdBg:hUOXawcwQGGG' # Прокси в одном из форматов [ip:port:login:password]
############################## SCRIPT MODE SETTINGS ##########################
mode = {
	'invite_to': False, 		# приглашение в группу|канал
	'channels': True, 			# спам по комментариям в публичных|приватных каналах
	'stories': False, 			# просмотр историй
	'dm': False 				# спам по лс
}
check_mode = {
	'Каналы': True,				# Проверка на вид объекта
	'Чаты': True,				# Можно указать несколько
	'Личные сообщения': False	# True ==> включено, False ==> выключено
}
to_change = {
	'avatar': False,
	'name_surname': False,
	'bio': False,
	'chatlists': False
}

# НЕ ТРОГАТЬ
mode = [x for x in mode if mode[x]][0]
check_mode = [{'Каналы': InputPeerChannel, 'Чаты': InputPeerChat, 'Личные сообщения': InputPeerUser}[x] for x in check_mode if check_mode[x]]

_proxy = (proxy.split(':') if '@' not in proxy else f'http://{proxy}') if proxy else None
proxies = {'http://': _proxy if '@' in proxy else f'http://{_proxy[2]}:{_proxy[3]}@{_proxy[0]}:{_proxy[1]}', 'https://': _proxy if '@' in proxy else f'http://{_proxy[2]}:{_proxy[3]}@{_proxy[0]}:{_proxy[1]}'} if proxy else None
############################## MODE - CHANNELS | DM ###############################
if mode in 'channels|dm':
	generate_text = True	# Переключение генерации текста через chatgpt
	openai_api_key = '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'	# API ключ от openai
	gpt_dialog_story = [{"role": "system", "content": "Ты девушка. И пишеш кратко, до 11 слов."}]	# Диалог с чатгпт до создания сообщения для поста
	gpt_not_working_answer_variants = ['Даже не знаю, что тут сказать....']	# Варианты ответов когда чатгпт не ворк

	time_before_message = (1, 5) # Время в секундах перед отправкой сообщения
	default_message = [{'id': 5289586317645077510, 'access_hash': 7245844214166698113},{'id': 5289511688293338831, 'access_hash': 1137509983462803804},{'id': 5289535491002096295, 'access_hash': -3061125516054875403},{'id': 5289588898920419145, 'access_hash': 3573321663229533686},{'id': 5289906434442550104, 'access_hash': 4924521636611331134},{'id': 5289879955969169162, 'access_hash': 6310489662076477707},{'id': 5289796083847811471, 'access_hash': 8295482215025586400},{'id': 5289764408464004031, 'access_hash': -2803425084711759046},{'id': 5289702977546770586, 'access_hash': -510216593859876423},{'id': 5289989194167378432, 'access_hash': 7268345685988666182},{'id': 5289886505794293950, 'access_hash': -964833228214339290},{'id': 5289536766607385266, 'access_hash': -6456463453854177141},{'id': 5289986514107783641, 'access_hash': -3900350503390658286},{'id': 5289765168673216333, 'access_hash': 9222618895651619720},{'id': 5289633957422323878, 'access_hash': -7568303907346536467},'РАБОТАЕМ','РАБОТАЕМ.','Гринд.','ГРИНД.','База','БАЗА','гриндим','кайф'] 		# Текст для спама по умолчанию (если не указан текст для цели)
	spam_channels = {						# ID или название канала для спам (Если пусто, то выберутся все каналы на аккаунте)
		
	}

############################## MODE - STORIES #####################################
if mode in 'stories':
	parse_chats = [] 						# Откуда парсить истории со всех чатов (Если пусто, то выберутся все чаты на аккаунте)
	enable_likes = True 					# Лайкать просмотренные истории

############################## MODE - INVITE_TO #####################################
if mode in 'invite_to':
	parse_invites = ['Your Channel Name'] 						# ID или названия чатов в которые пригласить людей (Если пусто, то выберутся все чаты на аккаунте)
	parse_chats = ['туртлеинсуит(муфлоны)'] 						# Откуда приглашать людей
