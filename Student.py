class Student:

	def __init__(self):
		pass

	def get_statistics_grade(self, cursor):
		sum_grade = 0
		grade = []
		[grade.append(i[0]) for i in cursor]
		len_grade = len(grade)

		if len_grade == 0:
			return "Нету оценок"
		else:
			for i in grade:
				if i != ".":
					sum_grade += int(i)
			return sum_grade // len_grade

	def get_statistics_progress(self, cursor, date):
		progress = []
		list_date = date

		if list_date is not None:
			[progress.append(i[0]) for i in cursor]
			while "." in progress:
				progress.remove(".")
			kol_date = list_date.count("                 ")
			len_progress = len(progress)
			len_date = len(list_date) - kol_date
			return str(len_date*2 - len_progress*2) + "/" + str(len_date*2)
		else:
			return "Нет в подгруппе"