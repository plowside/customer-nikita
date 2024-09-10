import asyncio, asyncpg, json

from datetime import datetime
from typing import Optional, List, Dict, Any
from config import db_config

class AsyncPostgresDB:
	def __init__(self):
		self.pool = None

	async def init_pool(self):
		self.pool = await asyncpg.create_pool(
			user=db_config['user'],
			password=db_config['password'],
			database=db_config['dbname'],
			host=db_config['host'],
			port=db_config['port']
		)
		await self.create_tables()

	async def close_pool(self):
		await self.pool.close()

	async def create_tables(self):
		table_queries = {
			'users': '''
				CREATE TABLE IF NOT EXISTS users(
					id SERIAL PRIMARY KEY,
					uid BIGINT,
					username TEXT,
					first_name TEXT,
					registration_date BIGINT,
					referral_from_id BIGINT,
					balance FLOAT DEFAULT 0,
					ref_balance FLOAT DEFAULT 0,
					is_banned BOOL DEFAULT False
				)
			''',
			'transactions_refill': '''
				CREATE TABLE IF NOT EXISTS transactions_refill(
					id SERIAL PRIMARY KEY,
					uid BIGINT,
					transaction_id TEXT,
					issue_date BIGINT,
					payment_service_name TEXT,
					payment_amount FLOAT
				)
			''',
			'banned': '''
				CREATE TABLE IF NOT EXISTS banned(
					id SERIAL PRIMARY KEY,
					uid BIGINT,
					issue_date BIGINT,
					ban_reason TEXT,
					unban_ts BIGINT DEFAULT 0
				)
			''',
			'smm_data': '''
				CREATE TABLE IF NOT EXISTS smm_data(
					name TEXT,
					data TEXT
				)
			''',
			'orders': '''
				CREATE TABLE IF NOT EXISTS orders(
					id SERIAL PRIMARY KEY,
					uid BIGINT,
					order_id BIGINT,
					order_url TEXT,
					order_orig_price FLOAT,
					order_orig_price_per_one FLOAT,
					order_price FLOAT,
					order_price_per_one FLOAT,
					order_amount BIGINT,
					order_category_name TEXT,
					order_service_name TEXT,
					order_service_id TEXT,
					order_status BIGINT DEFAULT (0),
					unix BIGINT
				)
			''',
			'promocodes': '''
				CREATE TABLE IF NOT EXISTS promocodes(
					id SERIAL PRIMARY KEY,
					promocode_id TEXT,
					promocode_maxuses BIGINT,
					promocode_reward FLOAT,
					promocode_type BIGINT,
					promocode_activated_uids TEXT,
					promocode_is_active BOOL DEFAULT True
				)
			''',
			'discounts': '''
				CREATE TABLE IF NOT EXISTS discounts(
					id SERIAL PRIMARY KEY,
					uid BIGINT,
					promocode_id BIGINT,
					discount_maxuses BIGINT,
					discount_amount BIGINT,
					discount_activations_counter BIGINT DEFAULT (0),
					discount_is_active BOOL DEFAULT True
				)
			'''
		}
		async with self.pool.acquire() as conn:
			for table_name, q in table_queries.items():
				await conn.execute(q)

	@staticmethod
	def format_sql(**kwargs):
		i = 1
		query = []
		values = []
		for x in kwargs:
			if not kwargs[x]: continue
			query.append(f"{x} = ${i}")
			values.append(kwargs[x])
			i+=1
		return ', '.join(query), values


	async def release_connection(self, conn):
		await self.pool.release(conn)

	async def execute(self, query: str, *args):
		async with self.pool.acquire() as conn:
			result = await conn.execute(query, *args)
		return result

	async def fetch(self, query: str, *args) -> List[Dict[str, Any]]:
		async with self.pool.acquire() as conn:
			result = await conn.fetch(query, *args)
		return [dict(record) for record in result]

	async def fetchrow(self, query: str, *args) -> Optional[Dict[str, Any]]:
		async with self.pool.acquire() as conn:
			result = await conn.fetchrow(query, *args)
		return dict(result) if result else None

	async def fetchval(self, query: str, *args) -> Optional[Any]:
		async with self.pool.acquire() as conn:
			result = await conn.fetchval(query, *args)
		return result


db = AsyncPostgresDB()