import sqlite3


class Databases:
	def __init__(self):
		self.db = sqlite3.connect("bntu_db.db")
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
	def create_table_group(self, group):
		self.cursor_db.execute(f"CREATE TABLE group{group}(name)")
		self.db.commit()

	def create_table_statement(self, group):
		self.cursor_db.execute(f""" CREATE TABLE statement{group}(
									name text,
									date text,
									value text
								) """)
		self.db.commit()

# update
	def set_info_update(self, table, condition_column, condition_data):
		self.cursor_db.execute(f"UPDATE {table} SET {condition_column} WHERE {condition_data}")
		self.db.commit()

# update replace like
	def set_info_update_replace_like(self, a, b, c, d, e, f, g):
		self.cursor_db.execute(f"UPDATE {a} SET {b} = REPLACE({c}, '{d}', '{e}') WHERE {f} LIKE '%{g}%'")
		self.db.commit()

# alter
	def set_alter_info_group(self, group, group_new):
		self.cursor_db.execute(f"ALTER TABLE group{group} RENAME TO group{group_new}")
		self.db.commit()

# join
	def get_info_join(self, name, date, group):
		return self.cursor_db.execute(f"""
					SELECT value 
					FROM statement{group} 
					JOIN group{group} ON '{date}' = statement{group}.date 
					AND '{name}' = statement{group}.name
					""")

# delete
	def delete_info_statement(self, name, date, group):
		self.cursor_db.execute(f"DELETE FROM statement{group} WHERE name = '{name}' AND date = '{date}'")
		self.db.commit()

# drop
	def drop_table(self, number):
		self.cursor_db.execute(f"DROP TABLE group{number}")
		self.cursor_db.execute(f"DELETE FROM group_db WHERE num_group = '{number}'")
		self.cursor_db.execute(f"DROP TABLE statement{number}")
		self.db.commit()

	def drop_teachers_student(self, table, condition):
		self.cursor_db.execute(f"DELETE FROM {table} WHERE {condition}")
		self.db.commit()
