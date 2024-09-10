import asyncio, hashlib, logging, httpx, copy, time
from cashews import cache

from config import *

cache.setup('mem://')
####################################################################
gpf = [x[-3:-2] for x in sets_categories if x.startswith('__')]
def rpf(s):
	for x in gpf: s = s.replace(x, '')
	return s
def cpf(s):
	if s.startswith('__'): return True
	for x in gpf:
		if x in s: return False
	return True

# Получить хэш строки
@cache(ttl=None)
async def get_hash(text):
	return hashlib.md5(text.encode('utf-8')).hexdigest()



class services_soc_proof:
	def __init__(self):
		self.base_url = 'https://partner.soc-proof.su/api/v2'
		self.hashs = {}
		self.all_data = {'category_name': {}, 'category_type': {}, 'category_type_hash': {}, 'services': {}, 'min_price': {}}

	async def _post(self, url, params = {}):
		async with httpx.AsyncClient(params={'key': soc_proof_api}, timeout=180) as client:		
			return await client.post(url, params=params)

	@cache(ttl=None)
	async def get_services(self, hashed=False):
		if hashed:
			ts = time.time()
			original_services = (await self._post(self.base_url, params={'action': 'services'})).json()
			ts_2 = time.time()

			main_cats = {}
			cats = {}
			services = {}

			for x in copy.deepcopy(original_services):
				for c in delete_emoji: x['category'] = x['category'].replace(c, '')
				if x['category'] not in cats:
					cats[x['category']] = {x['service']: x}
				else:
					cats[x['category']][x['service']] = x


			for category_type in cats:
				for category_name in ['twitter', 'telegram', 'instagram', 'facebook', 'youtube', 'vk', 'tiktok', 'rutube', 'onlyfans', 'discord', 'яндекс.дзен', 'yappy', 'spotify', 'web', 'likee', 'reddit', 'shazam', 'private', 'linkedin', 'snapchat', 'soundcloud', 'одноклассники', 'twitch', 'apple music', 'социальные сигналы']:
					if len([service for service in cats[category_type] if category_name in cats[category_type][service]['category'].lower()]) > 0:
						if category_name in main_cats:
							main_cats[category_name].append(category_type)
							services[category_name][category_type] = cats[category_type]
						else:
							main_cats[category_name] = [category_type]
							services[category_name] = {category_type: cats[category_type]}
						category_type_hash = (await get_hash(f'{category_name}_{category_type}'))[:10]
						category_type_value = services[category_name].pop(category_type)
						self.all_data['category_type'][f'{category_name}_{category_type}'] = category_type_hash
						self.all_data['category_type_hash'][f'{category_name}_{category_type_hash}'] = category_type
						self.all_data['min_price'][category_type_hash] = None
						self.hashs[category_type_hash] = category_type_value
						services[category_name][category_type_hash] = category_type_value
						
						for service in dict(services[category_name][category_type_hash]):
							if len(sets_accepted_services) > 0:
								if int(service) not in sets_accepted_services:
									del services[category_name][category_type_hash][service]
									continue
							obj = services[category_name][category_type_hash][service]
							obj['service_id'] = int(obj['service'])
							obj['rate'] = float(obj['rate'])
							obj['price'] = float(obj['rate']/1000)
							obj['min'] = int(obj['min'])
							obj['max'] = int(obj['max'])


							obj['service_id'] = int(obj['service'])
							obj['min'] = int(obj['min'])
							obj['max'] = int(obj['max'])
							obj['rate'] = float(obj['rate'])
							if obj['max'] > 1:
								obj['price'] = float(obj['rate']/1000)
							else:
								obj['price'] = float(obj['rate'])
							price = round(float(obj['price']) + float(obj['price']) * extra_price_percent, 3)
							self.all_data['services'][service] = obj
							if not self.all_data['min_price'][category_type_hash]:
								self.all_data['min_price'][category_type_hash] = price
							elif price < self.all_data['min_price'][category_type_hash]:
								self.all_data['min_price'][category_type_hash] = price

						if category_type_hash in services[category_name] and len(services[category_name][category_type_hash]) == 0:
							del services[category_name][category_type_hash]
						break

			print(f'Время на запрос: {round(ts_2 - ts, 2)} сек. | Время на обработку данных: {round(time.time() - ts_2, 2)} сек. | Общая разница: {round(time.time() - ts, 2)} сек.\n')
		else:
			try:
				original_services = (await self._post(self.base_url, params={'action': 'services'})).json()
				main_cats = {}
				cats = {}
				services = {}

				for x in copy.deepcopy(original_services):
					for c in delete_emoji: x['category'] = x['category'].replace(c, '')
					if x['category'] not in cats:
						cats[x['category']] = {x['service']: x}
					else:
						cats[x['category']][x['service']] = x


				for category_type in cats:
					for category_name in ['twitter', 'telegram', 'instagram', 'facebook', 'youtube', 'vk', 'tiktok', 'rutube', 'onlyfans', 'discord', 'яндекс.дзен', 'yappy', 'spotify', 'web', 'likee', 'reddit', 'shazam', 'private', 'linkedin', 'snapchat', 'soundcloud', 'одноклассники', 'twitch', 'apple music', 'социальные сигналы']:
						if len([service for service in cats[category_type] if category_name in cats[category_type][service]['category'].lower()]) > 0:
							if category_name in main_cats:
								main_cats[category_name].append(category_type)
								services[category_name][category_type] = cats[category_type]
							else:
								main_cats[category_name] = [category_type]
								services[category_name] = {category_type: cats[category_type]}

							for service in dict(services[category_name][category_type]):
								if len(sets_accepted_services) > 0:
									if int(service) not in sets_accepted_services:
										del services[category_name][category_type][service]
										continue
								obj = services[category_name][category_type][service]
								obj['service_id'] = int(obj['service'])
								obj['rate'] = float(obj['rate'])
								obj['price'] = float(obj['rate']/1000)
								obj['min'] = int(obj['min'])
								obj['max'] = int(obj['max'])


								obj['service_id'] = int(obj['service'])
								obj['min'] = int(obj['min'])
								obj['max'] = int(obj['max'])
								obj['rate'] = float(obj['rate'])
								if obj['max'] > 1:
									obj['price'] = float(obj['rate']/1000)
								else:
									obj['price'] = float(obj['rate'])
							
							if category_type in services[category_name] and len(services[category_name][category_type]) == 0:
								del services[category_name][category_type]
							break
			except Exception as e:
				logging.error(f'[services_smmcode] Не удалось получить сервисы: {e}')
				raise e

		return services

	async def create_order(self, service_id, amount, url):
		req = await self._post(self.base_url, params={'action': 'add', 'service': service_id, 'quantity': amount, 'link': url})
		return req.json()

	@cache(ttl='10s')
	async def get_order(self, order_id):
		req = await self._post(self.base_url, params={'action': 'status', 'order': order_id})
		return req.json()
	
	async def get_orders(self, orders_id):
		req = await self._post(self.base_url, params={'action': 'status', 'orders': ','.join([str(x) for x in orders_id])})
		return req.json()

	@cache(ttl='1m')
	async def get_balance(self):
		req = await self._post(self.base_url, params={'action': 'balance'})
		return req.json()

	@cache(ttl=None)
	async def decode(self, category_type_hash = None):
		if category_type_hash not in self.hashs:
			await self.get_services(True)
	
		return self.hashs[category_type_hash]

	async def get_service_data(self, category_name = None, category_type = None, category_type_hash = None, service_id = None):
		if service_id: return self.all_data['services'][service_id]
		elif category_type_hash: return self.all_data['category_type_hash'][category_type_hash]
		elif category_type: return self.all_data['category_type'][category_type]
		elif category_name:
			services = await self.get_services()
			return services[category_name]


####################################################################
ssf_client = services_soc_proof()



async def main():
	req = await ssf_client.get_services(True)
	print(req)


if __name__ == '__main__':
	asyncio.run(main())