### GENERAL ###
bot_token = '6511242030:AAHigCR99AOqCZcz6AE0wDU2pcOG6RgimS8' # токен бота
admin_ids = [6315225351, 1488282589] # id админов
clients_ttl = 3600 # Время работы сессии в секундах (завершится когда не будет задач), запускаются при новой задаче
reports_range = (20, 60) # Промежуток в секундах между отправками репортов

sessions = 'data/sessions' # Путь до сессии
proxies = 'data/proxy.txt' # Путь до прокси
proxy_protocol = {'http': True, 'socks5': False} # Протокол прокси


report_objs = {
	'user':		'👤 Пользователь',
	'bot':		'🤖 Бот',
	'channel':	'📢 Канал',
	#'message':	'✉️ Сообщение',
	#'avatar':	'🖼 Аватарка',
	#'story':	'🏞 История',
}
report_reasons = {
	'spam':				'Спам',
	'violence':			'Насилие',
	'child_abuse':		'Детская порнография',
	'pornography':		'Порнография',
	'copyright':		'Авторские права',
	'illegal_drugs':	'Наркотики',
	'personal_details': 'Личные данные',
	'other':			'Другое',
	'fake':				'Фейк',
	'geo_irrelevan':	'Расскрытие гео'
}
profiles = {
	'spam': {
		'imba_list': {
			'name': 'Имба список',
			'values': ['zdg', 'xcv']
		},
		'imba_list2': {
			'name': 'Имба список 2',
			'values': ['zdg', 'xcv']
		},
	},
	'violence': {

	},
	'child_abuse': {

	},
	'pornography': {

	},
	'copyright': {

	},
	'illegal_drugs': {

	},
	'personal_details': {

	},
	'other': {

	},
	'fake': {

	},
	'geo_irrelevan'	: {

	}
}