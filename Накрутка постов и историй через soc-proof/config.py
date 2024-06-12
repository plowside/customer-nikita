### GENERAL ###
bot_token = '6511242030:AAH0IxAhjb1lguWBjHeMHl2SikkEIUgq8vs' # Токен тг бота для лога. Брать у @botfather
log_chat_id = -4229870813 # ID чата в который отсылать лог
session = 'data/main_session.session' # Путь до сессии
target_channels = { # Каналы на которые нужно накручивать. Формат: ID_канала: 'ссылка на канал'
	-1002046287809: 'https://t.me/StalnoyX',
	-1002082364358: 'https://t.me/CodecsP',
	-1002170178180: 'https://t.me/testplow',
	-1002103652482: 'https://t.me/vetrovconsultant'
}
target_channels_strategy = { # Стратегии накрутки для каждого канала. Формат id_канала: стратегия накрутки
	-1002046287809: {
		'post': { # Тип накрутки: пост
			'service_id': 272,	# ID сервиса накрутки. Написано в описании сервиса
			'strategy': [
				{'time_before_start': 0, 'count': 400},
				{'time_before_start': 0, 'count': 400},
				{'time_before_start': 0, 'count': 400},
				{'time_before_start': 0, 'count': 400},
			]
		},
		'story': { # Тип накрутки: история
			'service_id': 602,	# ID сервиса накрутки. Написано в описании сервиса
			'strategy': [
				{'time_before_start': 0, 'count': 400},
				{'time_before_start': 0, 'count': 400},
				{'time_before_start': 0, 'count': 400},
				{'time_before_start': 0, 'count': 400},
			]
		}
	},
	-1002082364358: {
		'post': {
			'service_id': 272,	# ID сервиса накрутки. Написано в описании сервиса
			'strategy': [
				{'time_before_start': 0, 'count': 400},
				{'time_before_start': 0, 'count': 400},
				{'time_before_start': 0, 'count': 400},
				{'time_before_start': 0, 'count': 400},
			]
		},
		'story': {
			'service_id': 602,	# ID сервиса накрутки. Написано в описании сервиса
			'strategy': [
				{'time_before_start': 0, 'count': 400},
				{'time_before_start': 0, 'count': 400},
				{'time_before_start': 0, 'count': 400},
				{'time_before_start': 0, 'count': 400},
			]
		}
	},
	-1002170178180: {
		'post': {
			'service_id': 272,	# ID сервиса накрутки. Написано в описании сервиса
			'strategy': [
				{'time_before_start': 0, 'count': 400},
				{'time_before_start': 0, 'count': 400},
				{'time_before_start': 0, 'count': 400},
				{'time_before_start': 0, 'count': 400},
			]
		},
		'story': {
			'service_id': 602,	# ID сервиса накрутки. Написано в описании сервиса
			'strategy': [
				{'time_before_start': 0, 'count': 400},
				{'time_before_start': 0, 'count': 400},
				{'time_before_start': 0, 'count': 400},
				{'time_before_start': 0, 'count': 400},
			]
		}
	},
	-1002103652482: {
		'post': {
			'service_id': 272,	# ID сервиса накрутки. Написано в описании сервиса
			'strategy': [
				{'time_before_start': 0, 'count': 400},
				{'time_before_start': 0, 'count': 400},
				{'time_before_start': 0, 'count': 400},
				{'time_before_start': 0, 'count': 400},
			]
		},
		'story': {
			'service_id': 602,	# ID сервиса накрутки. Написано в описании сервиса
			'strategy': [
				{'time_before_start': 0, 'count': 400},
				{'time_before_start': 0, 'count': 400},
				{'time_before_start': 0, 'count': 400},
				{'time_before_start': 0, 'count': 400},
			]
		}
	}
}

### SOC-PROOF ###
soc_proof_api_token = '92a9c719850a60133e53b0a115019346' # Апи ключ от soc-proof.su
soc_proof_services = {
	# Накрутка на посты
	'post': {
		'enabled': True, # True - включено | False - выключено
	},
	# Накрутка на истории
	'story': {
		'enabled': True, # True - включено | False - выключено
	}
}