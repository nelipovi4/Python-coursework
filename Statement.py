import calendar
import datetime


class Statement:
	def __init__(self):
		pass

	def check_which_value(self, cursor_db):
		unique_results = set()

		for row in cursor_db:
			unique_results.add(row)

		if not unique_results:
			return "."
		else:
			for row in unique_results:
				return row[0]
