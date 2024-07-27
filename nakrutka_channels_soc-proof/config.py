### GENERAL ###
bot_token = '7306244866:AAEMdvdTKMz3GemnnB39xXMG9UtQdaq7Ghk' # Токен тг бота для лога. Брать у @botfather
admin_ids = [6315225351] # ID админов, которым будет отвечать бот
log_chat_id = 6315225351 # ID чата в который отсылать лог

target_channels = { # Каналы на которые нужно накручивать. Формат: ID_канала: 'ссылка на канал'
	-1002046287809: 'https://t.me/StalnoyX',
	-1002082364358: 'https://t.me/CodecsP',
	-1002170178180: 'https://t.me/testplow',
	-1002103652482: 'https://t.me/vetrovconsultant'
}
target_channels_strategy = { # Стратегии накрутки для каждого канала. Формат id_канала: стратегия накрутки
	-1002046287809: {
		'channel': { # Тип накрутки: пост
			'strategy': [
				{'time_before_start': 10, 'count': 400},
				{'time_before_start': 20, 'count': 400},
			]
		}
	},
	-1002082364358: {
		'channel': {
			'strategy': [
				{'time_before_start': 0, 'count': 400},
				{'time_before_start': 0, 'count': 400},
				{'time_before_start': 10, 'count': 400},
			]
		}
	},
	-1002170178180: {
		'channel': {
			'strategy': [
				{'time_before_start': 0, 'count': 400},
				{'time_before_start': 125, 'count': 400},
				{'time_before_start': 0, 'count': 400},
				{'time_before_start': 10, 'count': 400},
			]
		}
	},
	-1002103652482: {
		'channel': {
			'strategy': [
				{'time_before_start': 0, 'count': 400},
				{'time_before_start': 125, 'count': 400},
				{'time_before_start': 10, 'count': 400},
				{'time_before_start': 634, 'count': 400},
			]
		}
	}
}


### SOC-PROOF ###
soc_proof_api_token = '45eda3c20c442d85cf14007449988168' # Апи ключ от soc-proof.su
soc_proof_services = {'channel': {'enabled': True, 'service_id': 235}}#