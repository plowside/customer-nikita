# -*- coding: UTF-8 -*-
import traceback, datetime, logging, asyncio, sqlite3, random, httpx, socks, json, time, re, os


from config import *

##############################################################################
logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s', level=logging.INFO)
logging.getLogger('httpx').setLevel(logging.WARNING)

version = 1.0
##############################################################################


def get_unix():
	return int(time.time())

def os_delete(*paths):
	for path in paths:
		try:
			os.remove(path)
			break
		except: ...




async def check_version():
	try:
		async with httpx.AsyncClient() as client:
			resp = (await client.get('https://customer-nikita.vercel.app')).json()
			if version != resp['autosubscribers']:
				logging.warning(f'\n\n\nДоступна новая версия скрипта: {resp["autosubscribers"]} | Скачать: https://github.com/plowside/customer-nikita\n\n\n')
	except:
		...





class sessions_manager:
	def __init__(self, main_session):
		self.lock = asyncio.Lock()

	# Выполнитель задач
	async def tasks_watcher(self):
		async with self.lock:
			tasks = cur.execute('SELECT * FROM tasks WHERE task_status = ?', ['in_progress']).fetchall()
		for task in tasks:
			match task['task_type']:
				case 'set_reaction':
					task['task_data'] = json.loads(task['task_data'])
					await self.async_create_task(self.task_executor(task))
		await asyncio.sleep(10)

		while True:
			async with self.lock:
				tasks = cur.execute('SELECT * FROM tasks WHERE task_status = ?', ['created']).fetchall()
			for task in tasks:
				match task['task_type']:
					case 'set_reaction':
						task['task_data'] = json.loads(task['task_data'])
						await self.async_create_task(self.task_executor(task))

			await asyncio.sleep(5)



	async def join_channel(self, client, client_data, task_id_text, target):
		try:
			try: await client(JoinChannelRequest(target))
			except: await client(ImportChatInviteRequest(target.replace('+', '').replace('https://t.me/', '')))
			return True
		except rpcerrorlist.UserNotParticipantError:
			return True
		except rpcerrorlist.InviteRequestSentError:
			return True
		except rpcerrorlist.FloodWaitError:
			logging.info(f'[{task_id_text}|{client_data.id}] Антифлуд')
			return False
		except rpcerrorlist.ChannelPrivateError:
			logging.info(f'[{task_id_text}|{client_data.id}] Канал приватный либо пользователь заблокирован в нём')
			return False
		except rpcerrorlist.InviteHashExpiredError:
			logging.info(f'[{task_id_text}|{client_data.id}] Невалидная ссылка')
			return None
		except Exception as e:
			return False
	
	async def leave_channel(self, client, client_data, task_id_text, target):
		try:
			try: await client.delete_dialog((await client.get_entity(target)).id)
			except ValueError: ...
			except: await client(LeaveChannelRequest(target))
			return True
		except rpcerrorlist.FloodWaitError:
			logging.info(f'[{task_id_text}|{client_data.id}] Антифлуд')
			return False
		except rpcerrorlist.ChannelPrivateError:
			logging.info(f'[{task_id_text}|{client_data.id}] Канал приватный либо пользователь заблокирован в нём')
			return False
		except rpcerrorlist.InviteHashExpiredError:
			logging.info(f'[{task_id_text}|{client_data.id}] Невалидная ссылка')
			return None
		except rpcerrorlist.UserNotParticipantError:
			return True
		except:
			return False


	async def task_executor(self, task):
		async with self.lock:
			cur.execute('UPDATE tasks SET task_status = ? WHERE id = ?', ['in_progress', task['id']])
			con.commit()

		task_data = task['task_data']
		link = task_data['link']
		task_id_text = f"{task_data['channel_id']}|{task_data['message_id']}"
		task_completed = True
		channel_id = task_data['channel_id']
		channel_data = channels[channel_id]
		sessions_count = random.randint(*channel_data['sessions'])
		clients = list(self.clients.items())[:sessions_count]

		time_to_sleep_i = [] 
		temp = sessions_count
		temp3 = 0
		for i_, x in enumerate(channel_data['strategy']):
			if temp <= 0: break
			temp2 = x[1]
			temp3 += x[1]
			if temp2 > temp: temp2 = temp
			time_to_sleep_i.append([temp3, x[0] / temp2])
			temp -= x[1]
		reactions = {x: (80 if x == task_data['start_reaction'] else 30) for x in channel_data['reactions']}
		for i, (client, client_data) in enumerate(clients, start=1):
			if random.random() < chances['skip_session']:
				continue

			time_to_sleep = 10
			for x in time_to_sleep_i:
				if i <= x[0]:
					time_to_sleep = x[1]
					break
			try:
				reaction = random.choices(list(reactions.keys()), list(reactions.values()))[0]
				await client(functions.messages.SendReactionRequest(peer=task_data['link'], msg_id=task_data['message_id'], big=True, add_to_recent=False, reaction=[types.ReactionCustomEmoji(int(reaction)) if reaction.isnumeric() else types.ReactionEmoji(reaction)]))
				logging.info(f'[{task_id_text}|{client_data.id}] Установил реакцию {reaction}')
			except rpcerrorlist.FloodWaitError:
				logging.info(f'[{task_id_text}|{client_data.id}] Антифлуд')
			except rpcerrorlist.ChannelPrivateError:
				logging.error(f'[{task_id_text}|{client_data.id}] Канал приватный либо пользователь заблокирован в нём')
			except Exception as e:
				logging.error(f'[{task_id_text}|{client_data.id} | LINE:{traceback.extract_tb(e.__traceback__)[-1].lineno}] Общая ошибка ({type(e)}): {e}\n{traceback.format_exc()}')
			
			if len(clients) != i:
				await asyncio.sleep(time_to_sleep)


		async with self.lock:
			cur.execute('UPDATE tasks SET task_status = ? WHERE id = ?', ['completed' if task_completed else 'created', task['id']])
			con.commit()
		logging.info(f'[{task_id_text}|{client_data.id}] Задача завершена')

	async def async_create_task(self, task):
		asyncio.get_event_loop().create_task(task)







async def main():
	await check_version()
	await proxy_client.proxy_check()

	client = sessions_manager(main_session)
	await client.init_main_session()
	
	for session in sessions:
		await client.init_session(session)

	if len(client.clients) == 0:
		logging.info('Нет сессий для работы')
		exit()

	await client.tasks_watcher()
	await asyncio.Event().wait()

if __name__ == '__main__':
	proxy_client = ProxyManager(proxies)
	asyncio.run(main())