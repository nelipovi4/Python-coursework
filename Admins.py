
class Admins:
	def get_list(self, cursor_db):
		list_num_group = []

		for i in cursor_db:
			list_num_group.extend(i)

		return list_num_group