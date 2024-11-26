class Teachers:

	def __init__(self):
		self.list_name_global = []

	def get_list_group(self, lists):
		list_num = []
		for i in lists:
			num_group_str = i[0]
			list_num = num_group_str.replace(',', ' ').split()
		return list_num

	def get_list_name(self, lists):
		list_num_name = []
		for i in lists:
			list_num_name.extend(i)
		return list_num_name

	def get_str(self, cursor_db):
		text = ''

		for i in cursor_db:
			text += i[0]

		return text


