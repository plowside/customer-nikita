### GENERAL ###
delete_bad_sessions = True # Удалять невалидные сессии. (True — да | False — нет)

sessions = 'data/sessions' # Путь до сессий
proxies = 'data/proxy.txt' # Путь до прокси
proxy_protocol = {'http': True, 'socks5': False} # Протокол прокси
avatars_path = 'data/avatars' # Путь до аватарок
remove_avatar_after_use = False # Удалять использованную аватарку. (True — да | False — нет)


# Планировщики задач (Постоянно выполняют определенную задачу с определенным промежутком по времени)
schedulers = {
	'avatar_update': {'days': (1, 10), 'hours': (0, 6), 'minutes': (0, 60), 'seconds': (0, 60)}
}