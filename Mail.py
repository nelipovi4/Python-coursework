import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os


class Mail:
	def send_email(self, subject, body, to_email, attachment_file_paths):
		""" Отправка email с вложениями. """
		from_email = "zhenya.nelipovich@gmail.com"
		password = "zpow cova rbkh rkel"

		# Убедимся, что адрес получателя правильный
		to_email = str(to_email).strip().strip('<>').replace("'", "").replace('"', '')

		# Создание сообщения
		msg = MIMEMultipart()
		msg['From'] = from_email
		msg['To'] = to_email
		msg['Subject'] = subject

		msg.attach(MIMEText(body, 'plain'))

		try:
			with open(attachment_file_paths, 'rb') as attachment:
				# Получаем только имя файла без пути
				filename = os.path.basename(attachment_file_paths)

				# Создание части для вложения
				part = MIMEBase('application', 'octet-stream')
				part.set_payload(attachment.read())
				encoders.encode_base64(part)
				part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
				msg.attach(part)
		except Exception as e:
			print(f"Ошибка при добавлении вложения {attachment_file_paths}: {e}")

		try:
			# Настройка соединения с Gmail SMTP сервером
			server = smtplib.SMTP('smtp.gmail.com', 587)
			server.starttls()  # Шифрование
			server.login(from_email, password)  # Логинимся с паролем приложения
			server.send_message(msg)
			server.quit()
			print("Email sent successfully!")
		except Exception as e:
			print(f"Failed to send email: {e}")


