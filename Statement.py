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
			return " ."
		else:
			for row in unique_results:
				len_row = len(row[0])
				if len_row == 1:
					return f" {row[0]}"
				else:
					return f"{row[0]}"

	def check_which_value_practice(self, cursor_db):
		unique_results = set()

		for row in cursor_db:
			unique_results.add(row)

		if not unique_results:
			return "      ."
		else:
			for row in unique_results:
				try:
					if int(row[0]) > 9:
						return f" {row[0]} | {row[1]}"
					else:
						return f"   {row[0]} | {row[1]}"
				except:  # может произойти ошибка, если там встретится '.'
					return f"   {row[0]} | {row[1]}"

	def get_list_date(self, lists):
		list_nn_date = ["                 ", "                 ",
		"                 ", "                 ",
		"                 ", "                 "]
		len_lists = len(lists)
		lists.sort()

		if len_lists <= 6:
			for i in range(len_lists):
				list_nn_date[i] = lists[i]
		else:
			list_nn_date = []
			for i in range(len_lists):
				list_nn_date.append(lists[i])
			while len(list_nn_date) % 6 != 0:
				list_nn_date.append("                 ")
		return list_nn_date

	def get_list_week(self, dates):
		days_of_week = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
		weekdays = []

		for date_str in dates:
			if date_str != "                 ":
				date_obj = datetime.datetime.strptime(date_str, "%d.%m.%Y")
				# Получаем день недели (0 = Пн, 6 = Вс)
				day_of_week = date_obj.weekday()
				weekdays.append(days_of_week[day_of_week])
			else:
				weekdays.append("  ")
		return weekdays
