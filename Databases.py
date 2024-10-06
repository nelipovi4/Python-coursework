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
	def insert_info_values_one(self, a, b):
		self.cursor_db.execute(f"INSERT INTO '{a}' VALUES('{b}')")
		self.db.commit()

	def insert_info_values_six(self, a, b, c, d, e, f):
		self.cursor_db.execute(f"INSERT INTO {a} VALUES('{b}', '{c}','{d}', '{e}', '{f}', 'None')")
		self.db.commit()

# create
	def create_table_group(self, a):
		self.cursor_db.execute(f"CREATE TABLE group{a}(name)")

# update
	def set_info_update_five(self, a, b, c, d, e):
		self.cursor_db.execute(f"UPDATE {a} SET {b}='{c}' WHERE {d}='{e}'")
		self.db.commit()

	def set_info_update_nine(self, a, b, c, d, e, f, g, h, i):
		self.cursor_db.execute(f"UPDATE {a} SET {b}='{c}', {d}='{e}',{f}='{g}' WHERE {h}='{i}'")
		self.db.commit()

	def set_info_update_thirteen(self, a, b, c, d, e, f, g, h, i, j, k, l, m):
		self.cursor_db.execute(
			f"UPDATE {a} SET {b}='{c}', {d}='{e}', "
			f"{f}='{g}', {h}='{i}', "
			f"{j} ='{k}' WHERE {l}={m}")
		self.db.commit()

	def set_info_update_replace_like(self, a, b, c, d, e, f, g):
		self.cursor_db.execute(f"UPDATE {a} SET {b} = REPLACE({c}, '{d}', '{e}') WHERE {f} LIKE '%{g}%'")
		self.db.commit()

# alter
	def set_alter_info_group(self, a, b):
		self.cursor_db.execute(f"ALTER TABLE group{a} RENAME TO group{b}")
		self.db.commit()
