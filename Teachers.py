class Teachers:

	def __init__(self):
		self.list_name_global = []

	def set_list_name_global(self, lists):
		self.list_name_global = self.get_list_name(lists)

	def get_list_name_global(self):
		return self.list_name_global

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
