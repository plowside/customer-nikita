import asyncio, json, os

from telethon.sync import TelegramClient
from telethon import types
from telethon import events


os.makedirs('sessions', exist_ok=True)
#try: os.remove('telethon_session')
#except: ...
with TelegramClient('telethon_session', 24507152, '917d917ebdac58f757b115f24bb37bc4', system_lang_code='ru', system_version='4.16.30-vxCUSTOM') as client:
	me = client.get_me()

os.rename('telethon_session.session', f'sessions/{me.id}.session')
print(f'Сессия успешно создана\nФайл: {me.id}.session')