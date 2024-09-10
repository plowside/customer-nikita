import sqlite3, os, json, psycopg2
from config import db_config

def DB_DictFactory(cursor, row):
	_ = {}
	for i, column in enumerate(cursor.description):
		_[column[0]] = row[i]
	return _



if os.path.exists('db.db'):
	sqlite_connection = sqlite3.connect('db.db')
	sqlite_cursor = sqlite_connection.cursor()
	sqlite_cursor.row_factory = DB_DictFactory


postgres_connection = psycopg2.connect(
	**db_config
)
postgres_cursor = postgres_connection.cursor()
table_queries = {
	'users': '''
		CREATE TABLE IF NOT EXISTS users(
			id SERIAL PRIMARY KEY,
			uid BIGINT,
			username TEXT,
			first_name TEXT,
			registration_date BIGINT,
			referral_from_id BIGINT,
			balance DECIMAL DEFAULT 0,
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
			payment_amount DECIMAL
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
			order_orig_price DECIMAL,
			order_orig_price_per_one DECIMAL,
			order_price DECIMAL,
			order_price_per_one DECIMAL,
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
			promocode_reward DECIMAL,
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
	''',
}

# Создание таблиц в PostgreSQL
for table_name, query in table_queries.items():
	postgres_cursor.execute(query)


zxc = {True: 'true', False: 'false'}



if os.path.exists('db.db'):
	for table_name in table_queries.keys():
		sqlite_cursor.execute(f'SELECT * FROM {table_name}')
		rows = sqlite_cursor.fetch()

		for row in rows:
			if table_name == 'users':
				try:
					if row['referral_from_id'] == '': del row['referral_from_id']
					else: row['referral_from_id'] = int(row['referral_from_id'])
				except: del row['referral_from_id']
				
				row['is_banned'] = bool(row['is_banned'])
				row['first_name'] = row['first_name'].replace("'",'').replace('"','')
				
				if row['username'] == 'none' or row['username'] == None: del row['username']
				if row['first_name'] == 'none' or row['first_name'] == None: del row['first_name']


			elif table_name == 'promocodes':
				row['promocode_is_active'] = bool(row['promocode_is_active'])

			elif table_name == 'discounts':
				row['discount_is_active'] = bool(row['discount_is_active'])


			xcv = ', '.join(['%s'  for x in row])
			xcv_v = [row[x] if 'TEXT' in table_queries[table_name].split(x)[1].split('\n')[0] else zxc[row[x]] if type(row[x]) == bool else str(row[x]) for x in row]

			postgres_cursor.execute(f'INSERT INTO {table_name} ({", ".join(row.keys())}) VALUES ({xcv})', xcv_v)
	sqlite_connection.close()

postgres_connection.commit()
postgres_connection.close()