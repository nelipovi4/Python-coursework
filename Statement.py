import datetime


class Statement:
	def __init__(self):
		self.today = datetime.date.today()
		self.formatted_date = self.today.strftime('%d.%m.%Y')

	def get_today_date(self):
		return self.formatted_date

	def check_which_value(self, cursor_db):
		unique_results = set()

		for row in cursor_db:
			unique_results.add(row)

		if not unique_results:
			return "."
		else:
			for row in unique_results:
				return row[0]

	def get_weekdays(self, date_string):
		day, month, year = map(int, date_string.split('.'))
		input_date = datetime.date(year, month, day)

		# Найдем понедельник недели, в которую входит введенная дата
		start_of_week = input_date - datetime.timedelta(days=input_date.weekday() + 1)

		weekdays = []
		for i in range(7):
			current_date = start_of_week + datetime.timedelta(days=i+1)
			weekdays.append(current_date.strftime('%d.%m.%Y'))
		return weekdays
