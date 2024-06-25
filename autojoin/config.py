### GENERAL ###
bot_token = '7306244866:AAEMdvdTKMz3GemnnB39xXMG9UtQdaq7Ghk' # Токен тг бота для лога. Брать у @botfather
bot_recipients = [6315225351] # ID получателей сообщений в боте
main_session = 'data/6315225351.session' # Путь до "главной" сессии, с которой будет происходить поиск новых задач (Эта сессия не будет участвовать в накрутке)
main_channel = {'id': -1002103010424, 'link': 'https://t.me/+2rcHv9Xcxxw4ODU6'}
delete_bad_sessions = True # Удалять невалидные сессии. (True — да | False — нет)

sessions = 'data/sessions' # Путь до сессий
proxies = 'data/proxy.txt' # Путь до прокси
proxy_protocol = {'http': True, 'socks5': False} # Протокол прокси
to_write_usernames = 'data/to_write_usernames.txt' # Путь до юзернеймов пользователей, которым каждая сессия должна писать каждый день
to_write_text = 'data/to_write_text.txt' # Путь до текста, который каждая сессия должна писать каждый день
sessions_avatars = 'data/avatars' # Путь до аватарок сессий

sender_exceptions = [777000] # тг ID пользователей, от которых не принимать сообщения

# Планировщики задач (Постоянно выполняют определенную задачу с определенным промежутком по времени)
schedulers = {
	'send_message_contact': {'days': (0, 0), 'hours': (12, 12), 'minutes': (0, 0), 'seconds': (0, 0)},
	'set_online': {'days': (0, 0), 'hours': (2, 4), 'minutes': (0, 5), 'seconds': (0, 0)},
	'avatar_update': {'days': (2, 2), 'hours': (0, 0), 'minutes': (0, 0), 'seconds': (0, 0)},
}
# Шансы для выполнения действия
chances = {
	'read_new_post': 20,
}
# Задержки до\после действий (before — до | after — после)
delays = {
	'after_join__con': (4, 10),
	'after_leave__discon': (0, 0),
	'between_join_and_leave__allcon': (2, 2),
	'online_time': (30, 70),
	'online_before_message_read': (5, 3600),
	'before_message_read': (2, 4)
}