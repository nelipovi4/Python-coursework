import sqlite3

"""
cursor_db.execute( 0 CREATE TABLE teachers(
	name text,
	login text,
	password text,
	items text,
	num_group text,
	email text
) 0 )

"""

db = sqlite3.connect("bntu_db.db")

cursor_db = db.cursor()

# teachers group10701123 group_db statement10701123

# cursor_db.execute("SELECT rowid, * FROM teachers")

# cursor_db.execute("INSERT INTO teachers VALUES()")

# print(cursor_db.fetchall())

# cursor_db.execute("UPDATE teachers SET password='123' WHERE rowid=0")

#cursor_db.execute("UPDATE teachers SET items = REPLACE(items, 'БД', 'ЯП') WHERE items LIKE '%БД%'")

#for i in cursor_db:
	#print(i)

cursor_db.execute("ALTER TABLE teachers ADD settings text")

#cursor_db.execute(f"""SELECT value FROM statement_practice10701123 WHERE name='Аронова Е.A' AND date='21.10.2024' """)

#cursor_db.execute(f"""SELECT value, subgroup FROM statement_practice10701123 WHERE name='Нелипович Е.Г' AND date='20.10.2024'""")




db.commit()
db.close()