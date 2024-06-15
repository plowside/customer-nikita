### GENERAL ###
bot_token = '6511242030:AAH0IxAhjb1lguWBjHeMHl2SikkEIUgq8vs' # Токен тг бота для лога. Брать у @botfather
bot_recipients = [1679518666, 1488282589, 7044387239, 5892870427] # ID получателей сообщений в боте
main_session = 'data/main_session.session' # Путь до "главной" сессии, с которой будет происходить поиск новых задач (Эта сессия не будет участвовать в накрутке)
main_channel = {'id': -1002103010424, 'link': 'https://t.me/+2rcHv9Xcxxw4ODU6'}
delete_bad_sessions = True # Удалять невалидные сессии. (True — да | False — нет)

sessions = 'data/sessions' # Путь до сессий
proxies = 'data/proxy.txt' # Путь до прокси
proxy_protocol = {'http': True, 'socks5': False} # Протокол прокси
to_write_usernames = 'data/to_write_usernames.txt' # Путь до юзернеймов пользователей, которым каждая сессия должна писать каждый день
sessions_avatars = 'data/avatars' # Путь до аватарок сессий

# Планировщики задач (Постоянно выполняют определенную задачу с определенным промежутком по времени)
schedulers = {
	'set_online': {'day': 0, 'hour': 3, 'minute': 0, 'second': 0},
	'send_message_contact': {'day': 0, 'hour': 12, 'minute': 0, 'second': 0},
}
# Шансы для выполнения действия
chances = {
	'read_new_post': 20,
}
# Задержки до\после действий (before — до | after — после)
delays = {
	'after_join_through_link': (4, 10),

}








version = '1.0'