### GENERAL ###
bot_token = '7306244866:AAEMdvdTKMz3GemnnB39xXMG9UtQdaq7Ghk' # Токен тг бота для лога. Брать у @botfather
admin_ids = [6315225351] # ID админов, которым будет отвечать бот
log_chat_id = 6315225351 # ID чата в который отсылать лог
proxies = 'data/proxy.txt' # Путь до прокси
proxy_protocol = {'http': True, 'socks5': False} # Протокол прокси
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
			'strategy': [
				{'time_before_start': 0, 'count': 400},
			]
		},
		'story': { # Тип накрутки: история
			'strategy': [
				{'time_before_start': 0, 'count': 400},
			]
		}
	},
	-1002082364358: {
		'post': {
			'strategy': [
				{'time_before_start': 0, 'count': 400},
			]
		},
		'story': {
			'strategy': [
				{'time_before_start': 0, 'count': 400},
			]
		}
	},
	-1002170178180: {
		'post': {
			'strategy': [
				{'time_before_start': 0, 'count': 400},
			]
		},
		'story': {
			'strategy': [
				{'time_before_start': 0, 'count': 400},
			]
		}
	},
	-1002103652482: {
		'post': {
			'strategy': [
				{'time_before_start': 0, 'count': 400},
			]
		},
		'story': {
			'strategy': [
				{'time_before_start': 0, 'count': 400},
			]
		}
	}
}


### SOC-PROOF ###
soc_proof_api_token = '92a9c719850a60133e53b0a115019346' # Апи ключ от soc-proof.su
soc_proof_services = {'post': {'enabled': True, 'service_id': 272}, 'story': {'enabled': True, 'service_id': 602}}#