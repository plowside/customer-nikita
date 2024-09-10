import json
from telethon.tl.types import *
config = json.loads(open('config.json', encoding='utf-8').read())
data_dict = config
data_dict_b = {}