################## ОСНОВНАЯ КОНФИГУРАЦИЯ ##################
bot_token = '6511242030:AAH0IxAhjb1lguWBjHeMHl2SikkEIUgq8vs' # Токен бота. Получать у @botfather
admin_ids = [5892870427, 1488282589, 7238365539, 1777045453, 6315225351] # ID админов через запятую. Пример: [6315225351, 5157674407]

project_start_ts = 1710115200 # Старт проекта

antiflood_limit = .5 # Время в секундах для срабатывания антифлуда
antiflood_text = '<b>❗️ Пожалуйста, не спамьте.</b>' # Текст при срабатывании антифлуда

extra_price_percent = 30 # Наценка на услуги в процентах
referral_percent = 10 # Количество процентов с реферала
min_ref_withdraw = 1000 # Минималка на вывод с реф. баланса в рублях

alert_min_balance = 200 # Предупреждение о минимальном балансе на смм панели
users_messages = { # Сообщения для пользователей в особых ситуациях
	'panel_balance_up': '<b>Проблема решена</b>\n\nПроблемы с провайдером услуг решены, можете снова заказать услугу.', # Когда баланс панели пополнен, но до этого юзер пытался купить, но ему выдало ошибку с проблемой провайдера
}
channels_to_check = [{'id': -1002103010424, 'title': '📢 PENIS NEWS', 'url': 'https://t.me/uikw23g4eruyf8itgbq2w38iryogb'}] # ID каналов в которые нужно вступить

db_config = {
	'dbname': 'neondb',
	'password': '67tmlwCpdvTH',
	'user': 'neondb_owner',
	'host': 'ep-blue-poetry-a2mdh1v7.eu-central-1.aws.neon.tech',
	'port': 5432
}
################## СОЦ. СЕТИ И т.д. ##################
url_administrator = 'https://t.me/GrindAdm' # Ссылка на администратора (Информация ==> Кнопка: Администратор)
url_support = 'https://t.me/GrindAdm' # Ссылка на саппорта (Информация ==> Кнопка: ⚙️ Техническая поддержка)
url_our_projects = 'https://t.me/GrindProjects' # Ссылка на ваши проекты (Информация ==> Кнопка: 🔗 Все проекты)
url_rules = 'https://telegra.ph/Pravila-07-11-152' # Ссылка на правила (Информация ==> Кнопка: 📖 Правила)
username_support = '@GrindAdm' # юзернейм поддержки бота



images = { # Пути до изображений
	'start_msg': r'images/start_msg.jpg', # /start
	'main_menu': r'images/main_menu.jpg', # Информация
	'user_menu': r'images/user_menu.jpg', # Профиль
	'smm_menu': r'images/smm_menu.jpg' # ⭐️ Заказать накрутку
}

advert_button_data = {'row_width': 1,
	'buttons': {
		'💸 Купить рекламу': f'url^{url_administrator}',
	}
} # row_width - количество кнопок на одной строке -||- Нет рекламы: {'❌ Закрыть': 'cd^utils:delete'} | Есть реклама: {'Текст кнопки': 'url^ссылка'}
################## ПЛАТЁЖНЫЕ СИСТЕМЫ ##################
payment_life_time = 240 # Время жизни платежа в минутах
payment_check_time = 420 # Время проверки платежа в минутах

# Включение платежных системы
payment_services = { # True - включено, False - выключено
	'crystalpay': False,
	'telegram': False,
	'aaio': True,
	'payok': False
}
payment_services_names = { # Названия платежных систем (Формат ==> 'системное название':'название для пользователя')
	'crystalpay': 'CrystalPay | Маркет | USDT и другие',
	'telegram': 'Telegram | Карты',
	'aaio': 'СБП | Карты | USDT и другие',
	'payok': 'Payok | Карты | USDT и другие'
}


# crystalpay.io
crystalpay_login = 'plowside' # Логин/название кассы
crystalpay_secret = '83c0ee6e720cc22a6acd612bfc275e12aae4ff8a' # Secret 1
crystalpay_description = 'Пополнение в KILLA SMM' # Описание платежа, которое будет видеть пользователь

# telegram
telegram_token = '1744374395:TEST:0a6c902c9d2e2ed93b61' # Токен оплаты у @BotFather
telegram_title = 'Пополнение в KILLA SMM' # Название платежа, которое будет видеть пользователь
telegram_description = 'Пополнение баланса' # Описание платежа, которое будет видеть пользователь
telegram_currency = 'rub' # Валюта платежа (https://core.telegram.org/bots/payments#supported-currencies)
telegram_photo = None # Ссылку на изображение в платеже (Именно ссылку, пример: https://example.com/invoce_photo.png)

# aaio.so
aaio_api = 'OTNlZmEzMTAtMzMxNy00ZjI4LTk0ODktYTBmMDU5YTYzNDFmOkpAYm9IM194VHM5dCVhMEArbnRGTXVNTSomU2t0MUhT' # API ключ
aaio_shop_id = '79928219-e2b6-4e25-9c83-1f384a32cb58' # Shop ID
aaio_secret_1 = 'e68a6a1c1e8e2d19270916e72ffe31a8' # Secret 1
aaio_secret_2 = '9a4ee333fa78a599c707a536ad4677a9' # Secret 2
aaio_description = 'Пополнение в Boost MCA' # Описание платежа, которое будет видеть пользователь
aaio_currency = 'RUB' # Валюта платежа (RUB, UAH, USD, EUR)



# payok.io
payok_shop = '7802' # Shop name
payok_secret = '' # Secret
payok_api = '8B2126E8EAF609234A7F3DF2267F3008-3C521D8A2BEC98AF396E969896FFF3B4-1B0655063EFF4AAD8EC9813714D59506' # API ключ
payok_api_id = '5548' # API ID
payok_io_currency = 'RUB' # Валюта платежа (RUB, UAH, USD, EUR)



payment_warn_limits = { # Минимальная сумма пополнения, не проходя которую пользователь будет получать предупреждение, но выдаст ссылку на пополнение
	'crystalpay': 0,
	'telegram': 0,
	'payok': 100,
	'aaio': 0
}

payment_cancel_limits = { # Минимальная сумма пополнения, не проходя которую пользователь будет получать отмену пополнения из-за ограничений платежки
	'crystalpay': 0,
	'telegram': 0,
	'payok': 10,
	'aaio': 200
}

soc_proof_api = '9f61adfd83f6819a9f9a47a204340f41' # API ключ soc-proof.su



epp = { # Количество элементов на странице 
	'category': 6, # Категории
	'category_type': 8, # Тип услуги
	'service': 10 # Услуги
}

################## SMM SETTINGS ################
errors_text = {
	"error.incorrect_service_id": "Данная услуга больше не предоставляется, либо перенесена в другой раздел, попробуйте начать сначала.",
	"neworder.error.link": "Указана недействительная ссылка.",
	"neworder.error.min_quantity": "Минимальное кол-во указано в описании услуги.",
	"neworder.error.max_quantity": "Максимальное кол-во указано в описании услуги.",
	"neworder.error.not_enough_funds": "Проблемы со стороны провайдера, попробуйте позже."
}
sets_categories = { # 'название из api ответа': 'название для пользователя'
	'telegram': '🩵 Telegram',
	#'vk': '💙 VK',
	#'instagram': '🧡 Instagram',
	#'youtube': '❤ YouTube',
	#'tiktok': '🖤 TikTok',
	#'twitch': '💜 Twitch',
	#'discord': '🩷 Discord',
	#'rutube': '❤ Rutube',
	#'twitter': '🩵 Twitter',
	#'facebook': '💙 Facebook',
	#'одноклассники': '💛 Одноклассники',
#
	#'__main=!__': '🔥 Другие сервисы',
	#'!spotify': 'Spotify',
	#'!likee': 'Likee',
	#'!web': 'Трафик на вебсайт',
	#'!private': 'Private',
	#'!yappi': 'Yappi',
	#'!soundcloud': 'SoundCloud',
	#'!onlyfans': 'OnlyFans',
	#'!apple music': 'Apple Music',
	#'!shazam': 'Shazam',
	#'!snapchat': 'Snapchat',
	#'!яндекс.дзен': 'Яндекс Дзен',
	#'!linkedin': 'LinkedIn',
	#'!reddit': 'Reddit',
	#'!социальные сигналы': 'Соц. Сигналы',
}

order_statuses_emoji = {
	'Pending': '🟡', # В обработке
	'In progress': '🟡', # Выполняется
	'Processing': '🟡', # В очереди
	'Partial': '🔴', # Частично выполнено
	'Canceled': '🔴', # Не оплачено
	'Closed': '🔴', # Закрыто
	'Completed': '🟢', # Завершён
	3: '🟢', # Выполнено
	5: '🔴', # Отменено
	6: '🔴', # Ошибка
	8: '🔴', # Возврат платежа
	'Жду ответ от сервера': '⚪️', # Неизвестно
	'Не удалось получить ответ от сервера': '⚪️', # Неизвестно
	10: '🟡', # В очереди
	None: '🔴' # В остальных случаях
}
order_statuses = {'Pending': 'Рассматривается', 'In progress': 'Выполняется', 'Completed': 'Завершён', 'Partial': 'Отменён', 'Processing': 'В очереди', 'Closed': 'Отменён', 'Canceled': 'Отменён', 'Жду ответ от сервера': 'Жду ответ от сервера', 'Не удалось получить ответ от сервера': 'Не удалось получить ответ от сервера'}

delete_emoji = [
	'⭐',
	'📈',
	'🔥',
	'🤟',
	'🔞',
	' / просмотры / реакции ⟮ для поиска ⟯'

]
sets_banned_services = [ # ID сервисов которые не нужно отображать через запятую. Пример: [1, 2, 623, 91284, 42]

]
sets_accepted_services = [ # ID сервисов которые нужно отображать через запятую. Пример: [1, 2, 623, 91284, 42]
	1483,
	1478,
	1549,
	1550,
	1480,
	1545
]

sets_services = { # В боте будут только те типы категорий (сервисы), которые указаны тут, в таком формате: 'название из api ответа': 'название для пользователя'
	'podpisciki':'Подписчики',
	'premium-podpisciki':'Премиум подписчики',
	'podpisciki-po-stranam':'Подписчики по странам',
	'podpisciki-dlia-privatnyx-kanalov':'Подписчики для приватных каналов',
	'podpisciki-dlia-vyvoda-kanala-v-top':'Подписчики для вывода канала в ТОП',
	'podpisciki-dlia-botov':'Подписчики для ботов',
	'busty':'Бусты',
	'prosmotry-na-odin-post':'Просмотры на один пост',
	'prosmotry-na-odin-post-po-stranam':'Просмотры на один пост по странам',
	'prosmotry-ot-premium-polzovatelei':'Просмотры от премиум пользователей',
	'prosmotry-na-odin-post-so-statistikoi':'Просмотры на один пост со статистикой',
	'prosmotr-istorii':'Просмотр историй',
	'prosmotry-dlia-privatnyx-kanalov-na-odin-post':'Просмотры для приватных каналов на один пост',
	'avtoprosmotry-dlia-privatnyx-kanalov':'Автопросмотры для приватных каналов',
	'prosmotry-v-telescope':'Просмотры в Telesco.pe',
	'prosmotry-na-neskolko-postov':'Просмотры на несколько постов',
	'kommentarii-k-postam':'Комментарии к постам',
	'sobstvennye-kommentarii':'Собственные комментарии',
	'prosmotry-na-neskolko-postov-po-stranam':'Просмотры на несколько постов по странам',
	'avtoprosmotry-na-budushhie-posty-po-stranam':'Автопросмотры на будущие посты по странам',
	'prosmotry-na-neskolko-postov-so-statistikoi':'Просмотры на несколько постов со статистикой',
	'avtoprosmotry-na-budushhie-posty':'Автопросмотры на будущие посты по странам',
	'reakcii-na-post':'Позитивные реакции на пост',
	'premium-reakcii-na-post':'Премиум реакции на пост',
	'negativnye-reakcii-na-post':'Негативные реакции на пост',
	'reakcii-na-neskolko-postov':'Реакции на несколько постов',
	'avtoreakcii-na-budushhie-posty':'Автореакции на будущие посты',
	'golosovaniia-v-oprosax-po-nomeru-otveta':'Голосования в опросах (по номеру ответа)',
	'golosovaniia-v-oprosax':'Голосования в опросах (по номеру ответа)',
	'reposty-na-post-so-statistikoi':'Репосты на пост со статистикой',
	'reposty-na-post':'Репосты на пост со статистикой',
	'reposty-na-neskolko-postov':'Репосты на несколько постов',
	'avtoreposty-na-budushhie-posty':'Авторепосты на будущие посты',
	'zaloby-na-akkaunt':'Жалобы на аккаунт',
	'zaloby':'Жалобы на аккаунт',
	'zaloby-na-akkaunt-po-kategoriiam':'Жалобы на аккаунт по категориям',
	'podpisciki-na-akkaunt':'Подписчики на аккаунт',
	'ucastniki-v-gruppu-ili-pablik':'Участники в группу или паблик',
	'laiki-na-post-foto-i-video':'Лайки на пост, фото и видео',
	'laiki-na-neskolko-postov':'Лайки на несколько постов',
	'prosmotry-na-video-ili-klipy':'Просмотры на видео или клипы',
	'prosmotry-na-zapisi':'Просмотры на записи',
	'reposty':'Репосты',
	'kommentarii-na-post':'Комментарии на пост',
	'kommentarii-na-neskolko-postov':'Комментарии на несколько постов',
	'laiki-na-kommentarii':'Лайки на комментарии',
	'golosa-v-oprosy':'Голоса в опросы',
	'podarki':'Подарки',
	'avtolaiki-na-budushhie-zapisi':'Автолайки на будущие записи',
	'avtoreposty-na-budushhie-zapisi':'Авторепосты на будущие записи',
	'proslusivanie-pleilista':'Прослушивание плейлиста',
	'vk-play-live':'VK Play Live',
	'kompleksnoe-prodvizenie':'Комплексное продвижение',
	'zaloby-na-post-gruppu-akkaunt':'Жалобы',
	'podpisciki-dlia-zakrytyx-akkauntov':'Подписчики для закрытых аккаунтов',
	'laiki-na-post':'Лайки на пост',
	'igtv-laiki':'IGTV лайки',
	'laiki-dlia-rekomendacii':'Лайки для рекомендаций',
	'prosmotry-video':'Просмотры видео',
	'prosmotry-dlia-reels':'Просмотры для Reels',
	'igtv-prosmotry':'IGTV просмотры',
	'kommentarii':'Комментарии',
	'kommentarii-dlia-reels':'Комментарии для Reels',
	'zriteli-v-priamoi-efir':'Зрители в прямой эфир',
	'oxvat-pokazy-i-poseshhenie-profilia':'Охват, показы и посещение профиля',
	'soxranenie-foto-i-video':'Сохранение фото и видео',
	'prosmotry-istorii':'Просмотры историй',
	'reposty-istorii':'Репосты историй',
	'reposty-na-posty':'Репосты на посты',
	'golosovaniia-v-istorii':'Голосования в истории',
	'upominaniia-v-istoriiax':'Упоминания в историях',
	'perexody-po-ssylke-v-istorii':'Переходы по ссылке в истории',
	'avtolaiki-na-budushhie-posty':'Автолайки на будущие посты',
	'avtoprosmotry-na-budushhie-video':'Автопросмотры на будущие видео',
	'avtokommentarii-na-budushhie-posty':'Автокомментарии на будущие посты',
	'avtoreposty-na-budushhie-istorii':'Авторепосты на будущие истории',
	'avtoprosmotry-profilia':'Автопросмотры профиля',
	'zaloby-na-post':'Жалобы на пост',
	'prosmotry-na-video':'Просмотры на видео',
	'prosmotry-na-shorts-video':'Просмотры на Shorts видео',
	'casy-prosmotrov-dlia-bystrogo-podkliuceniia-monetizacii':'Часы просмотров (для быстрого подключения монетизации)',
	'dobavlenie-v-pleilisty':'Добавление в плейлисты',
	'zriteli-na-priamuiu-transliaciiu-live-stream':'Зрители на прямую трансляцию (Live Stream)',
	'laiki-dlia-priamogo-efira':'Лайки для прямого эфира',
	'laiki-dlia-shorts':'Лайки для Shorts',
	'laiki':'Лайки',
	'dizlaiki':'Дизлайки',
	'reakcii-dlia-priamogo-efira':'Реакции для прямого эфира',
	'sobstvennye-otvety-na-kommentarii':'Собственные ответы на комментарии',
	'laiki-na-posty':'Лайки на посты',
	'dizlaiki-na-kommentarii':'Дизлайки на комментарии',
	'laiki-na-budushhie-video':'Лайки на будущие видео',
	'dizlaiki-na-budushhie-video':'Дизлайки на будущие видео',
	'zaloby-na-video':'Жалобы на видео',
	'zaloby-na-kanal':'Жалобы на канал',
	'laiki-na-priamuiu-transliaciiu':'Лайки на прямую трансляцию',
	'laiki-na-neskolko-video':'Лайки на несколько видео',
	'prosmotry-na-video-po-stranam':'Просмотры на видео по странам',
	'soxranenie-video':'Сохранение видео',
	'sobstvennye-kommentarii-dlia-priamogo-efira':'Собственные комментарии для прямого эфира',
	'zriteli-na-strim':'Зрители на стрим',
	'avtoreposty-na-starye-video':'Авторепосты на старые видео',
	'uslugi-dlia-popadaniia-v-rekomendacii':'Услуги для попадания в рекомендации',
	'follovery':'Фолловеры',
	'reposty-reshares':'Репосты (Reshares)',
	'vyvod-v-top':'Вывод в ТОП',
	'reakcii':'Реакции',
	'prosmotry-tvitov':'Просмотры твитов',
	'retvity':'Ретвиты',
	'pokazy-i-oxvaty':'Показы и охваты',
	'golosovanie-po-ssylkam':'Голосование по ссылкам',
	'zakladki':'Закладки',
	'kliki-po-xestegam':'Клики по хэштегам',
	'kliki-po-profiliu':'Клики по профилю',
	'druzia-v-profil':'Друзья в профиль',
	'podpisciki-v-gruppu':'Подписчики в группу',
	'podpisciki-na-publicnuiu-stranicu':'Подписчики на публичную страницу',
	'emocii-na-posty':'Эмоции на посты',
	'zriteli-na-priamoi-efir':'Зрители на прямой эфир',
	'ocenka-stranic-reiting':'Оценка страниц, рейтинг',
	'druzia':'Друзья',
	'ucastniki-v-gruppu':'Участники в группу',
	'klassy-laiki':'Классы (лайки)',
	'podpisciki-na-profil':'Подписчики на профиль',
	'prosmotry':'Просмотры',
	'rekomendacii':'Рекомендации',
	'odobreniia':'Одобрения',
	'poiskovye-sistemy':'Поисковые системы',
	'socialnye-seti':'Социальные сети',
	'priamye-perexody':'Прямые переходы',
	'socialnye-signaly':'Социальные сигналы',
	'ctenie-statei':'Чтение статей',
	'prosmotr-video':'Просмотр видео',
	'reposty-v-socialnye-seti':'Репосты в социальные сети',
	'kliki-po-reklame':'Клики по рекламе',
	'podpisciki-na-pleilist':'Подписчики для плейлистов, подкастов',
	'proslusivanie':'Прослушивание',
	'ezemesiacnye-slusateli':'Ежемесячные слушатели',
	'soxraneniia-trekov-ili-albomov':'Сохранения треков или альбомов',
	'zaprosy-v-druzia':'Запросы в друзья',
	'podpisciki-na-server':'Подписчики на сервер',
	'podpisciki-na-server-onlain':'Подписчики на сервер ОНЛАЙН',
	'neavtorizovannye-zriteli-na-strim':'Неавторизованные зрители на стрим',
	'avtorizovannye-zriteli-na-strim':'Авторизованные зрители на стрим',
	'podpisciki-na-kanal':'Подписчики на канал',
	'laiki-upvotes-na-otvety':'Лайки (UpVotes) на ответы',
	'golosovaniia-dlia-posta':'Голосования для поста',
	'prosmotry-dlia-posta':'Просмотры для поста',
	'proslusivaniia-trekov':'Прослушивания треков',
	'twitter-nft-follovery':'Twitter NFT фолловеры',
	'instagram-nft-podpisciki':'Instagram NFT подписчики',
	'nft-laiki-v-tvitter':'NFT лайки в Твиттер',
	'nft-discord-ucastniki-na-server':'NFT Discord Участники на сервер',
	'nft-retvity-v-tvitter':'NFT ретвиты в Твиттер',
	'nft-laiki-na-neskolko-postov-v-instagram':'NFT лайки на несколько постов в Инстаграм',
	'nft-kommentarii-v-tvitter':'NFT комментарии в Твиттер',
	'nft-laiki-na-video-iutub':'NFT лайки на видео Ютуб',
	'ustanovka-prilozeniia-na-android':'Установка приложения на Android',
	'ustanovka-prilozeniia-na-ios':'Установка приложения на iOS',
	'golosa':'Голоса',
	'reposty-repin':'Репосты (repin)',
	'posetiteli':'Посетители',
	'otvety':'Ответы',
	'proslusivaniia':'Прослушивания',
	'applodismenty':'Апплодисменты',
	'dobavlenie-v-izbrannoe':'Добавление в избранное',
	'reakcii-na-kanal':'Реакции на канал',
	'ucastniki-dlia-gruppy':'Участники для группы',
	'proigryvaniia':'Проигрывания',
	'potoki':'Потоки',
	'dobavleniia-v-pleilist':'Добавления в плейлист',
	'popolneniia':'Пополнения',
	'otzyvy-i-kommentarii-2gis':'Отзывы и комментарии 2ГИС',
	'sobstvennye-otzyvy-i-kommentarii-2gis':'Собственные отзывы и комментарии 2ГИС',
	'sobstvennye-otzyvy-dlia-irecommend':'Собственные отзывы для iRecommend',
	'otzyvy-dlia-irecommend':'Отзывы для iRecommend',
	'otzyvy-dlia-iandeks-kart':'Отзывы для Яндекс карт',
	'sobstvennye-otzyvy-dlia-iandeks-kart':'Собственные отзывы для Яндекс карт',
	'otzyvy-dlia-zoon':'Отзывы для Zoon',
	'sobstvennye-otzyvy-dlia-zoon':'Собственные отзывы для Zoon'
}


################## НЕ ТРОГАТЬ ##################
extra_price_percent /= 100 # Перевод в проценты
referral_percent /= 100 # Перевод в проценты
sets_services_reverse = {sets_services[x]: x for x in sets_services}
promocode_types = {1: 'Деньги на баланс', 2: 'Скидка в %'}
channels_data = {}