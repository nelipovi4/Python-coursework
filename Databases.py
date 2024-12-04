import sqlite3


class Databases:
	def __init__(self):
		self.db = sqlite3.connect("bntu_db.db", check_same_thread=False)
		self.cursor_db = self.db.cursor()

# select
	def get_info_select_from(self, a, b):
		return self.cursor_db.execute(f"SELECT {a} FROM {b}")

	def get_info_select_from_where(self, a, b, c, d):
		return self.cursor_db.execute(f"SELECT {a} FROM {b} WHERE {c}='{d}'")

# insert
	def insert_info_values(self, table, value):
		self.cursor_db.execute(f"INSERT INTO {table} VALUES({value})")
		self.db.commit()

# create
	def create_table_group(self, group, id):
		self.cursor_db.execute(f"CREATE TABLE group{group}_{id}(name, subgroup)")
		self.db.commit()

	def create_table(self, group, value):
		self.cursor_db.execute(f"CREATE TABLE {group}({value})")
		self.db.commit()

	def create_table_statement(self, group, types):
		self.cursor_db.execute(f""" CREATE TABLE statement_{types}{group}(
									name text,
									date text,
									value text
								) """)
		self.db.commit()

	def create_table_statement_practice(self, group):
		self.cursor_db.execute(f""" CREATE TABLE statement_practice{group}(
									name text,
									date text,
									value text,
									subgroup text
								) """)
		self.db.commit()

# update
	def set_info_update(self, table, condition_column, condition_data):
		self.cursor_db.execute(f"UPDATE {table} SET {condition_column} WHERE {condition_data}")
		self.db.commit()

	def set_info_update_student(self, group, condition_column, condition_data):
		self.cursor_db.execute(f"UPDATE group{group} SET {condition_column} WHERE {condition_data}")
		self.cursor_db.execute(f"UPDATE statement_practice{group} SET {condition_column} WHERE {condition_data}")
		self.cursor_db.execute(f"UPDATE statement_lecture{group} SET {condition_column} WHERE {condition_data}")
		self.cursor_db.execute(f"UPDATE statement_consultation{group} SET {condition_column} WHERE {condition_data}")
		self.db.commit()

# update replace like
	def set_info_update_replace_like(self, a, b, c, d, e, f, g):
		self.cursor_db.execute(f"UPDATE {a} SET {b} = REPLACE({c}, '{d}', '{e}') WHERE {f} LIKE '%{g}%'")
		self.db.commit()

# alter
	def set_alter_info_group(self, group, group_new):
		self.cursor_db.execute(f"ALTER TABLE group{group} RENAME TO group{group_new}")
		self.cursor_db.execute(f"ALTER TABLE statement_lecture{group} RENAME TO statement_lecture{group_new}")
		self.cursor_db.execute(f"ALTER TABLE statement_consultation{group} RENAME TO statement_consultation{group_new}")
		self.cursor_db.execute(f"ALTER TABLE statement_practice{group} RENAME TO statement_practice{group_new}")
		self.cursor_db.execute(f"ALTER TABLE date_{group} RENAME TO date_{group_new}")
		self.db.commit()

# join
	def get_info_join(self, name, date, group, types):
		return self.cursor_db.execute(f"""
					SELECT value 
					FROM statement_{types}{group} 
					JOIN group{group} ON '{date}' = statement_{types}{group}.date 
					AND '{name}' = statement_{types}{group}.name
					""")
	
	def get_info_join_practice(self, name, date, group, types):
		return self.cursor_db.execute(f"""
					SELECT value, subgroup 
					FROM statement_{types}{group} 
					JOIN group{group} ON '{date}' = statement_{types}{group}.date 
					AND '{name}' = statement_{types}{group}.name
					""")

# delete
	def delete_info_statement(self, name, date, group, types):
		self.cursor_db.execute(f"DELETE FROM statement_{types}{group} WHERE name = '{name}' AND date = '{date}'")
		self.db.commit()

	def delete_teachers(self, table, condition):
		self.cursor_db.execute(f"DELETE FROM {table} WHERE {condition}")
		self.db.commit()

	def delete_student(self, group, condition):
		self.cursor_db.execute(f"DELETE FROM statement_lecture{group} WHERE {condition}")
		self.cursor_db.execute(f"DELETE FROM statement_consultation{group} WHERE {condition}")
		self.cursor_db.execute(f"DELETE FROM statement_practice{group} WHERE {condition}")
		self.cursor_db.execute(f"DELETE FROM group{group} WHERE {condition}")
		self.db.commit()

	def delete_all_value_table(self, table):
		self.cursor_db.execute(f"DELETE FROM {table}")
		self.db.commit()

# drop
	def drop_table(self, number):
		self.cursor_db.execute(f"DROP TABLE group{number}")
		self.cursor_db.execute(f"DELETE FROM group_db WHERE num_group = '{number}'")
		self.cursor_db.execute(f"DROP TABLE statement_lecture{number}")
		self.cursor_db.execute(f"DROP TABLE statement_consultation{number}")
		self.cursor_db.execute(f"DROP TABLE statement_practice{number}")
		self.cursor_db.execute(f"DROP TABLE date_{number}")
		self.db.commit()

