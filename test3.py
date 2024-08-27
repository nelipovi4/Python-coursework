import calendar
import datetime

# Получаем текущую дату
today = datetime.date.today()

# Получаем имя месяца
month_name = calendar.month_name[today.month]

print(f"Текущий месяц: {month_name}")
