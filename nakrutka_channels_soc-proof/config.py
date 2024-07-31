### GENERAL ###
bot_token = '7447039437:AAGfsA9eOYoIvYQLZ3eaGoY3hswoQWJb9Vs' # Токен тг бота для лога. Брать у @botfather
admin_ids = [1679518666, 5892870427, 1488282589, 6896954499] # ID админов, которым будет отвечать бот
log_chat_id = 6315225351 # ID чата в который отсылать лог

target_channels = { # Каналы на которые нужно накручивать. Формат: ID_канала: 'ссылка на канал'
	-1002046287809: 'https://t.me/goisclub',
	-1002082364358: 'https://t.me/sokratchanel',
	-1001811956441: 'https://t.me/miketysonp',
	-1002136518358: 'https://t.me/mantowern',
	-1001926801608: 'https://t.me/hokageknow',
	-1002244091569: 'https://t.me/slilok',


}
target_channels_strategy = { # Стратегии накрутки для каждого канала. Формат id_канала: стратегия накрутки
	-1002046287809: {
		'channel': { # Тип накрутки: пост
			'strategy': [
				{'time_before_start': (1000, 13000), 'count': (20, 25)},
				{'time_before_start': (1000, 16000), 'count': (20, 30)},
				{'time_before_start': (100, 8000), 'count': (20, 25)},
				{'time_before_start': (100, 9000), 'count': (20, 40)},
				{'time_before_start': (1000, 13000), 'count': (20, 25)},
				{'time_before_start': (1000, 15000), 'count': (20, 25)},
				{'time_before_start': (100, 3000), 'count': (20, 40)},
				{'time_before_start': (1000, 18000), 'count': (20, 30)},
				{'time_before_start': (1000, 13000), 'count': (20, 40)},
				{'time_before_start': (1000, 13000), 'count': (20, 30)},
				{'time_before_start': (100, 3000), 'count': (20, 35)},
				{'time_before_start': (1000, 13000), 'count': (20, 40)},
				{'time_before_start': (1000, 17000), 'count': (20, 35)},
				{'time_before_start': (1000, 13000), 'count': (20, 50)},
				{'time_before_start': (1000, 13000), 'count': (20, 25)},
				{'time_before_start': (3000, 13000), 'count': (20, 30)},
				{'time_before_start': (3100, 8000), 'count': (20, 25)},
				{'time_before_start': (100, 6000), 'count': (20, 25)},
				{'time_before_start': (1000, 11000), 'count': (20, 30)},
				{'time_before_start': (1000, 15000), 'count': (20, 40)},
				{'time_before_start': (1000, 9000), 'count': (20, 25)},
				{'time_before_start': (1000, 7000), 'count': (20, 30)},
				{'time_before_start': (1000, 16000), 'count': (20, 35)},
				{'time_before_start': (1000, 15000), 'count': (20, 40)},
				{'time_before_start': (1000, 14000), 'count': (20, 25)},
				{'time_before_start': (1000, 13000), 'count': (20, 30)},
				{'time_before_start': (100, 16000), 'count': (20, 30)},
				{'time_before_start': (1000, 13000), 'count': (20, 30)},
				{'time_before_start': (1000, 6000), 'count': (20, 30)},
				{'time_before_start': (1000, 13000), 'count': (20, 25)},
			]
		}
	},
	-1002082364358: {
		'channel': {
			'strategy': [
				{'time_before_start': (1000, 13000), 'count': (20, 40)},
				{'time_before_start': (1000, 16000), 'count': (20, 40)},
				{'time_before_start': (100, 8000), 'count': (20, 50)},
				{'time_before_start': (100, 9000), 'count': (20, 60)},
				{'time_before_start': (1000, 13000), 'count': (20, 40)},
				{'time_before_start': (1000, 15000), 'count': (20, 60)},
				{'time_before_start': (100, 3000), 'count': (20, 50)},
				{'time_before_start': (1000, 18000), 'count': (20, 40)},
				{'time_before_start': (1000, 13000), 'count': (20, 40)},
				{'time_before_start': (1000, 13000), 'count': (20, 40)},
				{'time_before_start': (100, 3000), 'count': (20, 400)},
				{'time_before_start': (1000, 13000), 'count': (20, 50)},
				{'time_before_start': (1000, 17000), 'count': (20, 50)},
				{'time_before_start': (1000, 13000), 'count': (20, 50)},
				{'time_before_start': (1000, 13000), 'count': (20, 60)},
				{'time_before_start': (3000, 13000), 'count': (20, 50)},
				{'time_before_start': (3100, 8000), 'count': (20, 40)},
				{'time_before_start': (100, 6000), 'count': (20, 40)},
				{'time_before_start': (1000, 11000), 'count': (20, 40)},
				{'time_before_start': (1000, 15000), 'count': (20, 40)},
				{'time_before_start': (1000, 9000), 'count': (20, 60)},
				{'time_before_start': (1000, 7000), 'count': (20, 70)},
				{'time_before_start': (1000, 16000), 'count': (20, 30)},
				{'time_before_start': (1000, 15000), 'count': (20, 35)},
				{'time_before_start': (1000, 14000), 'count': (20, 70)},
				{'time_before_start': (1000, 13000), 'count': (20, 30)},
				{'time_before_start': (100, 16000), 'count': (20, 40)},
				{'time_before_start': (1000, 13000), 'count': (20, 40)},
				{'time_before_start': (1000, 6000), 'count': (20, 40)},
				{'time_before_start': (1000, 13000), 'count': (20, 50)},
			]
		}
	},
	-1001811956441: {
		'channel': {
			'strategy': [
				{'time_before_start': (1000, 13000), 'count': (20, 25)},
				{'time_before_start': (1000, 16000), 'count': (20, 30)},
				{'time_before_start': (100, 8000), 'count': (20, 25)},
				{'time_before_start': (100, 9000), 'count': (20, 40)},
				{'time_before_start': (1000, 13000), 'count': (20, 25)},
				{'time_before_start': (1000, 15000), 'count': (20, 25)},
				{'time_before_start': (100, 3000), 'count': (20, 40)},
				{'time_before_start': (1000, 18000), 'count': (20, 30)},
				{'time_before_start': (1000, 13000), 'count': (20, 40)},
				{'time_before_start': (1000, 13000), 'count': (20, 30)},
				{'time_before_start': (100, 3000), 'count': (20, 35)},
				{'time_before_start': (1000, 13000), 'count': (20, 40)},
				{'time_before_start': (1000, 17000), 'count': (20, 35)},
				{'time_before_start': (1000, 13000), 'count': (20, 50)},
				{'time_before_start': (1000, 13000), 'count': (20, 25)},
				{'time_before_start': (3000, 13000), 'count': (20, 30)},
				{'time_before_start': (3100, 8000), 'count': (20, 25)},
				{'time_before_start': (100, 6000), 'count': (20, 25)},
				{'time_before_start': (1000, 11000), 'count': (20, 30)},
				{'time_before_start': (1000, 15000), 'count': (20, 40)},
				{'time_before_start': (1000, 9000), 'count': (20, 25)},
				{'time_before_start': (1000, 7000), 'count': (20, 30)},
				{'time_before_start': (1000, 16000), 'count': (20, 35)},
				{'time_before_start': (1000, 15000), 'count': (20, 40)},
				{'time_before_start': (1000, 14000), 'count': (20, 25)},
				{'time_before_start': (1000, 13000), 'count': (20, 30)},
				{'time_before_start': (100, 16000), 'count': (20, 30)},
				{'time_before_start': (1000, 13000), 'count': (20, 30)},
				{'time_before_start': (1000, 6000), 'count': (20, 30)},
				{'time_before_start': (1000, 13000), 'count': (20, 25)},
			]
		}
	},
	-1002136518358: {
		'channel': {
			'strategy': [
				{'time_before_start': (1000, 13000), 'count': (20, 40)},
				{'time_before_start': (1000, 16000), 'count': (20, 40)},
				{'time_before_start': (100, 8000), 'count': (20, 50)},
				{'time_before_start': (100, 9000), 'count': (20, 60)},
				{'time_before_start': (1000, 13000), 'count': (20, 40)},
				{'time_before_start': (1000, 15000), 'count': (20, 60)},
				{'time_before_start': (100, 3000), 'count': (20, 50)},
				{'time_before_start': (1000, 18000), 'count': (20, 40)},
				{'time_before_start': (1000, 13000), 'count': (20, 40)},
				{'time_before_start': (1000, 13000), 'count': (20, 40)},
				{'time_before_start': (100, 3000), 'count': (20, 400)},
				{'time_before_start': (1000, 13000), 'count': (20, 50)},
				{'time_before_start': (1000, 17000), 'count': (20, 50)},
				{'time_before_start': (1000, 13000), 'count': (20, 50)},
				{'time_before_start': (1000, 13000), 'count': (20, 60)},
				{'time_before_start': (3000, 13000), 'count': (20, 50)},
				{'time_before_start': (3100, 8000), 'count': (20, 40)},
				{'time_before_start': (100, 6000), 'count': (20, 40)},
				{'time_before_start': (1000, 11000), 'count': (20, 40)},
				{'time_before_start': (1000, 15000), 'count': (20, 40)},
				{'time_before_start': (1000, 9000), 'count': (20, 60)},
				{'time_before_start': (1000, 7000), 'count': (20, 70)},
				{'time_before_start': (1000, 16000), 'count': (20, 30)},
				{'time_before_start': (1000, 15000), 'count': (20, 35)},
				{'time_before_start': (1000, 14000), 'count': (20, 70)},
				{'time_before_start': (1000, 13000), 'count': (20, 30)},
				{'time_before_start': (100, 16000), 'count': (20, 40)},
				{'time_before_start': (1000, 13000), 'count': (20, 40)},
				{'time_before_start': (1000, 6000), 'count': (20, 40)},
				{'time_before_start': (1000, 13000), 'count': (20, 50)},
			]
		}
	},
	-1001926801608: {
		'channel': {
			'strategy': [
				{'time_before_start': (1000, 13000), 'count': (20, 40)},
				{'time_before_start': (1000, 16000), 'count': (20, 40)},
				{'time_before_start': (100, 8000), 'count': (20, 50)},
				{'time_before_start': (100, 9000), 'count': (20, 60)},
				{'time_before_start': (1000, 13000), 'count': (20, 40)},
				{'time_before_start': (1000, 15000), 'count': (20, 60)},
				{'time_before_start': (100, 3000), 'count': (20, 50)},
				{'time_before_start': (1000, 18000), 'count': (20, 40)},
				{'time_before_start': (1000, 13000), 'count': (20, 40)},
				{'time_before_start': (1000, 13000), 'count': (20, 40)},
				{'time_before_start': (100, 3000), 'count': (20, 400)},
				{'time_before_start': (1000, 13000), 'count': (20, 50)},
				{'time_before_start': (1000, 17000), 'count': (20, 50)},
				{'time_before_start': (1000, 13000), 'count': (20, 50)},
				{'time_before_start': (1000, 13000), 'count': (20, 60)},
				{'time_before_start': (3000, 13000), 'count': (20, 50)},
				{'time_before_start': (3100, 8000), 'count': (20, 40)},
				{'time_before_start': (100, 6000), 'count': (20, 40)},
				{'time_before_start': (1000, 11000), 'count': (20, 40)},
				{'time_before_start': (1000, 15000), 'count': (20, 40)},
				{'time_before_start': (1000, 9000), 'count': (20, 60)},
				{'time_before_start': (1000, 7000), 'count': (20, 70)},
				{'time_before_start': (1000, 16000), 'count': (20, 30)},
				{'time_before_start': (1000, 15000), 'count': (20, 35)},
				{'time_before_start': (1000, 14000), 'count': (20, 70)},
				{'time_before_start': (1000, 13000), 'count': (20, 30)},
				{'time_before_start': (100, 16000), 'count': (20, 40)},
				{'time_before_start': (1000, 13000), 'count': (20, 40)},
				{'time_before_start': (1000, 6000), 'count': (20, 40)},
				{'time_before_start': (1000, 13000), 'count': (20, 50)},
			]
		}
	},
	-1002244091569: {
		'channel': {
			'strategy': [
				{'time_before_start': (1000, 13000), 'count': (20, 25)},
				{'time_before_start': (1000, 16000), 'count': (20, 30)},
				{'time_before_start': (100, 8000), 'count': (20, 25)},
				{'time_before_start': (100, 9000), 'count': (20, 40)},
				{'time_before_start': (1000, 13000), 'count': (20, 25)},
				{'time_before_start': (1000, 15000), 'count': (20, 25)},
				{'time_before_start': (100, 3000), 'count': (20, 40)},
				{'time_before_start': (1000, 18000), 'count': (20, 30)},
				{'time_before_start': (1000, 13000), 'count': (20, 40)},
				{'time_before_start': (1000, 13000), 'count': (20, 30)},
				{'time_before_start': (100, 3000), 'count': (20, 35)},
				{'time_before_start': (1000, 13000), 'count': (20, 40)},
				{'time_before_start': (1000, 17000), 'count': (20, 35)},
				{'time_before_start': (1000, 13000), 'count': (20, 50)},
				{'time_before_start': (1000, 13000), 'count': (20, 25)},
				{'time_before_start': (3000, 13000), 'count': (20, 30)},
				{'time_before_start': (3100, 8000), 'count': (20, 25)},
				{'time_before_start': (100, 6000), 'count': (20, 25)},
				{'time_before_start': (1000, 11000), 'count': (20, 30)},
				{'time_before_start': (1000, 15000), 'count': (20, 40)},
				{'time_before_start': (1000, 9000), 'count': (20, 25)},
				{'time_before_start': (1000, 7000), 'count': (20, 30)},
				{'time_before_start': (1000, 16000), 'count': (20, 35)},
				{'time_before_start': (1000, 15000), 'count': (20, 40)},
				{'time_before_start': (1000, 14000), 'count': (20, 25)},
				{'time_before_start': (1000, 13000), 'count': (20, 30)},
				{'time_before_start': (100, 16000), 'count': (20, 30)},
				{'time_before_start': (1000, 13000), 'count': (20, 30)},
				{'time_before_start': (1000, 6000), 'count': (20, 30)},
				{'time_before_start': (1000, 13000), 'count': (20, 25)},
			]
		}
	}
}


### SOC-PROOF ###
soc_proof_api_token = '9f61adfd83f6819a9f9a47a20с4340f41' # Апи ключ от soc-proof.su
soc_proof_services = {'channel': {'enabled': True, 'service_id': 932}}#