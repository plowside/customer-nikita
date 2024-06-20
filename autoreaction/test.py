from telethon.sync import TelegramClient
from telethon import functions, types

with TelegramClient('data/sessions/7038303284.session', 69696969, 'qwertyuiopasdfghjklzxcvbnm1234567', flood_sleep_threshold=120, device_model='iPhone 15 Pro Max', system_version='4.16.30-vxCUSTOM', app_version='10.13.1', system_lang_code='en') as client:
    print(client.get_me())