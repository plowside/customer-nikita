### GENERAL ###
delete_bad_sessions = True # Удалять невалидные сессии. (True — да | False — нет)
main_session = 'data/6315225351.session' # Путь до "главной" сессии, с которой будет происходить поиск новых задач (Эта сессия не будет участвовать в накрутке)


text_to_answer = 'data/text.txt'
sessions = 'data/sessions' # Путь до сессий
channels = {
	-1002103010424: {
		'link': 'https://t.me/uikw23g4eruyf8itgbq2w38iryogb',
		'sessions': (40, 70),
		'reactions': [
			'👍',
			'😭',
			'😁'
		],
		'strategy': [
			[3600, 50],
			[86400, 50]
		]
	},
	-1002171071986: {
		'link': 'https://t.me/j3mgwferaw3',
		'sessions': (40, 70),
		'reactions': [
			'👍',
			'😭',
			'😁'
		],
		'strategy': [
			[3600, 50],
			[86400, 50]
		]
	}
}

time_to_answer = (3, 4) # Промежуток времени в секундах через которое бот должен ответить


proxies = 'data/proxy.txt' # Путь до прокси
proxy_protocol = {'http': True, 'socks5': False} # Протокол прокси


# Шансы для выполнения действия
chances = {
	'skip_session': 20,
}


# Обработка
chances = {key: value/100 for (key, value) in chances.items()}
#all_range = 0
#for i, x in enumerate(reaction_set_strategy):
#	all_range += x[1]
#	reaction_set_strategy[i][1] = all_range