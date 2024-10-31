from flet import *
import datetime
"""
    @ Задачи
        выделение по построчно в таблицах
        
        сделать обновить ПРАКТИКА
        добавить стрелки перемещение дат
        сделать кнопку "изменить даты"
        
        сделать для каждого преподавателя сделать БД
        проверку на добавлении одинаковых групп и студентов
        сделать Excel
        
        сделать долгое нажатие на ученика и показать там % посещаемости
        сделать аккаунт студента
"""
from Admins import Admins
from Databases import Databases
from Teachers import Teachers
from Statement import Statement
from Excel import Excel


class Main:
    def __init__(self, pageM):
        self.page = pageM
        self.db = Databases()
        self.page.title = "BNTU"
        self.page.vertical_alignment = MainAxisAlignment.CENTER

        # виджеты
        self.user_login = TextField(value="", width=300, text_align=TextAlign.LEFT, label="Логин", height=100,
                                    on_change=self.validate)
        self.user_password = TextField(value="", width=300, text_align=TextAlign.LEFT, label="Пароль", password=True,
                                       can_reveal_password=True, height=80, on_change=self.validate)
        self.btn_entry = ElevatedButton(text="Войти", disabled=True, width=300, height=50, bgcolor='#B0E0E6',
                                        color='black', on_click=self.check_users)

        # верхний бар
        self.page.appbar = AppBar(
            leading_width=20,
            title=Text("БНТУ | BNTU"),
            bgcolor=colors.SURFACE_VARIANT,
            actions=[
                IconButton(icons.SUNNY, on_click=self.change_topic),
                PopupMenuButton(
                    items=[
                        PopupMenuItem(text="Тех. поддержка"),
                    ]
                ),
            ],
        )

        # ряд
        self.page.add(
            Row(
                [
                    Column([
                        self.user_login,
                        self.user_password,
                        self.btn_entry
                    ])
                ], alignment=MainAxisAlignment.CENTER
            )
        )

# переход по темам
    def change_topic(self, e):
        if self.page.theme_mode == "light":
            self.page.theme_mode = 'dark'
            self.user_login.border_color = 'white'
            self.user_password.border_color = 'white'
        else:
            self.page.theme_mode = 'light'
            self.user_login.border_color = 'black'
            self.user_password.border_color = 'black'
        self.page.update()

# проверка, было что-то написано в логине и пароле
    def validate(self, e):
        if all([self.user_login.value, self.user_password.value]):
            self.btn_entry.disabled = False
        else:
            self.btn_entry.disabled = True
        self.page.update()

# аватар
    def avatar(self, name, id):
        self.page.clean()
        AccountTeachers(self.page, name, id, self.db)
        self.page.update()

# выход
    def logout(self):
        self.page.clean()
        Main(self.page)
        self.page.update()

# настройки
    def settings(self, id):
        self.page.clean()
        SettingsAdmin(self.page, self.db, id)

# проверка на вход
    def check_users(self, e):
        for i in self.db.get_info_select_from("rowid, login, password, name", "teachers"):
            if (f'{self.user_login.value}', f'{self.user_password.value}') == (i[1], i[2]):
                self.page.clean()
                if i[0] == 1:
                    self.page.appbar = AppBar(
                        leading_width=20,
                        title=Text(f"БНТУ | BNTU   {i[3]}"),
                        bgcolor=colors.SURFACE_VARIANT,
                        actions=[
                            IconButton(icons.SETTINGS, on_click=lambda event: self.settings(i[0])),
                            IconButton(icons.SUNNY, on_click=self.change_topic),
                            PopupMenuButton(
                                items=[
                                    PopupMenuItem(text="Тех. поддержка"),
                                    PopupMenuItem(text="Выход", on_click=lambda event: self.logout())
                                ]
                            ),
                        ],
                    )
                    self.page.update()
                    Admin(self.page, self.db)
                else:
                    self.page.appbar = AppBar(
                        leading_width=20,
                        title=Text(f"БНТУ | BNTU   {i[3]}"),
                        bgcolor=colors.SURFACE_VARIANT,
                        actions=[
                            IconButton(icons.ACCOUNT_CIRCLE_OUTLINED, on_click=lambda event: self.avatar(i[3], i[0])),
                            IconButton(icons.SUNNY, on_click=self.change_topic),
                            PopupMenuButton(
                                items=[
                                    PopupMenuItem(text="Тех. поддержка"),
                                    PopupMenuItem(text="Выход", on_click=lambda event: self.logout())
                                ]
                            ),
                        ],
                    )
                    self.page.update()
                    Numbers(self.page, i[0], self.db)


class Numbers:
    def __init__(self, pageN, id, db):
        self.page = pageN
        self.id = id
        self.db = db

        self.teacher = Teachers()
        self.statement = Statement()

        self.page.vertical_alignment = MainAxisAlignment.CENTER
        self.page.horizontal_alignment = CrossAxisAlignment.CENTER
        self.page.clean()
        self.page.update()
        self.click_cont()

# контейнеры и нажатие на них
    def click_cont(self):
        list_num = self.teacher.get_list_group(self.db.get_info_select_from_where("num_group", "teachers",
                                                                                  "rowid", self.id))
        for i in list_num:
            def next_class(e, value=i):
                self.page.clean()
                Visible(self.page, self.id, self.db, value, self.statement.get_today_date())

            self.page.add(
                Row(
                    [
                        Container(
                            content=Text(i, size=70),
                            margin=10,
                            padding=10,
                            alignment=alignment.center,
                            width=350,
                            height=150,
                            border_radius=10,
                            ink=True,
                            on_click=next_class,
                        ),
                    ],
                    alignment=MainAxisAlignment.CENTER,
                ),
            )


class Info:
    def __init__(self, pageN, id, db, value, today_date):
        self.page = pageN
        self.id = id
        self.db = db
        self.value = value
        self.date = today_date

        self.teacher = Teachers()
        self.statement = Statement()

        self.now = datetime.datetime.now()

        self.list_name = self.teacher.get_list_name(self.db.get_info_select_from("name", f"group{self.value}"))
        self.week_list = ['Имя', 'ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ']

        self.date_lecture = self.teacher.get_list_date(self.teacher.get_list_name(
            self.db.get_info_select_from_where("dates", f"date_{self.value}", "type", "lecture"))
        )
        self.date_consultation = self.teacher.get_list_date(self.teacher.get_list_name(
            self.db.get_info_select_from_where("dates", f"date_{self.value}", "type", "consultation"))
        )
        self.date_practice_1 = self.teacher.get_list_date(self.teacher.get_list_name(
            self.db.get_info_select_from("dates", f"date_{self.value} WHERE type='practice' AND subgroup='1'"))
        )
        self.date_practice_2 = self.teacher.get_list_date(self.teacher.get_list_name(
            self.db.get_info_select_from("dates", f"date_{self.value} WHERE type='practice' AND subgroup='2'"))
        )


class Card(Info):
    def __init__(self, pageN, id, db, value, today_date):
        super().__init__(pageN, id, db, value, today_date)
        self.card_container = None
        self.scroll_card = ListView(expand=1, spacing=10, padding=20, width=900, visible=False)

        self.create_card()

# кнопки для КАРТОЧКИ
        self.add_student_but = ElevatedButton(text="Добавить студента", width=300, height=50,
                                              bgcolor='#B0E0E6', color='black', on_click=self.fab_pressed,
                                              visible=False)
        self.add_file_but = ElevatedButton(text="Добавить данные через Excel", width=300, height=50,
                                           bgcolor='#B0E0E6', color='black', on_click=self.fab_pressed,
                                           visible=False)

# пункты
    def transition_class_edit(self, name):
        self.page.clean()
        EditStudent(self.page, self.db, name, self.value, 0)

    def delete_student(self, group, condition):
        self.db.delete_student(group, condition)
        self.scroll_card.controls.clear()
        self.create_card()
        self.page.update()

# кнопка добавление
    def fab_pressed(self, e):
        self.page.clean()
        AddStudent(self.page, self.db, self.value, self.id)

# Контейнеры для карточек
    def create_card(self):
        self.list_name = self.teacher.get_list_name(self.db.get_info_select_from("name", f"group{self.value}"))
        len_list = len(self.list_name)
        for i in range(len_list):
            self.card_container = Container(
                content=Column(
                    [
                        ListTile(
                            title=Text(f"{self.list_name[i]}", size=40),
                            leading=Icon(icons.ACCOUNT_BOX, size=50),
                            trailing=PopupMenuButton(
                                icon=icons.MORE_VERT,
                                items=[
                                    PopupMenuItem(text="Аккаунт",
                                                  on_click=lambda _, name=self.list_name[i]: print(name)),
                                    PopupMenuItem(text="Изменить",
                                                  on_click=lambda _, name=self.list_name[i]:
                                                  self.transition_class_edit(name)),
                                    PopupMenuItem(text="Удалить", on_click=lambda _, name=self.list_name[i]:
                                    self.delete_student(f"{self.value}", f"name='{name}'")),
                                ],
                                icon_size=35
                            ),
                        ),
                    ]
                ),
                width=600,
                padding=10,
                bgcolor=colors.SURFACE_VARIANT,
                border_radius=border_radius.all(15),
            )
            self.scroll_card.controls.append(self.card_container)


class TableLecture(Card):
    def __init__(self, pageN, id, db, value, today_date):
        super().__init__(pageN, id, db, value, today_date)

        self.scroll_table_lecture = ListView(expand=1, spacing=10, padding=15, width=1200)
        self.date_list = self.statement.get_weekdays(self.date)

        self.but_add_lecture = IconButton(icons.ADD_BOX,
                                    icon_size=35,
                                    tooltip="Добавить дату",
                                    icon_color="#31A52E",
                                    on_click=lambda e: self.add_date_lecture(e),
                                    )

        self.but_date_lecture = IconButton(icons.DATE_RANGE_ROUNDED,
                                     icon_size=35,
                                     tooltip="Изменить даты",
                                     icon_color="#31A52E",
                                     )
# Таблица с датами
        self.columns_table_lecture_date = [DataColumn(Text(f"{self.date_lecture[i]}", color="black", size=18)) for i in range(6)]

        self.table_lecture_date = DataTable(
            width=875,
            bgcolor="white",
            border=border.all(2, "#00FF7F"),
            border_radius=5,
            vertical_lines=BorderSide(2, "black"),
            columns=self.columns_table_lecture_date,
        )
        self.container_table_lecture_date = Container(
            Row([
                self.but_add_lecture,
                self.but_date_lecture,
                self.table_lecture_date,
            ], alignment=MainAxisAlignment.CENTER), padding=padding.only(left=180),
        )
# таблица основная
        self.columns_table_lecture = [DataColumn(Text(f"{self.week_list[i]}", color="black")) for i in range(7)]
        self.row_table_lecture = [  # i - строки | j - столбцы
            DataRow([
                DataCell(
                    Container(
                        content=Text(f"{self.list_name[i]}" if j == 0 else f"    {self.statement.check_which_value(
                            self.db.get_info_join(f"{self.list_name[i]}", f"{self.date_lecture[j - 1]}",
                                                  f"{self.value}", "lecture"))}",
                                     size=25, color="black"),
                        width=200 if j == 0 else None,
                        on_click=lambda e, n=j, a=i:
                        self.put_grade_student(self.date_lecture[n-1], self.list_name[a])
                        if n != 0 else None,
                    )
                )
                for j in range(7)
            ])
            for i in range(len(self.list_name))
        ]

        table_lecture = DataTable(
            width=800,
            bgcolor="white",
            border=border.all(2, "#00FF7F"),
            border_radius=5,
            vertical_lines=BorderSide(2, "black"),
            columns=self.columns_table_lecture,
            rows=self.row_table_lecture,
        )

        self.scroll_table_lecture.controls.append(table_lecture)

# всплывающее окна
        self.cancel = AlertDialog(
            title=Text("Данные не были обновлены", size=50, color="red"),
        )

        self.save = AlertDialog(
            title=Text("Успешно", size=50, color="green"),
        )

        self.error_date = AlertDialog(
            title=Text("Такая дата уже есть", size=50, color="red"),
        )

        self.banner = Banner(
                bgcolor=colors.AMBER_100,
                leading=Icon(icons.WARNING_AMBER_ROUNDED, color=colors.AMBER, size=40),
                content=Text(
                    value="Сперва добавьте дату",
                    color=colors.BLACK,
                    size=35
                ),
                actions=[
                    TextButton(text="Закрыть", on_click=lambda e: self.page.close_banner()),
                ],
            )

# radio button
        self.radio_group = RadioGroup(content=Row([
            Radio(value=" 1", label="1", tooltip="1 час пропуска"),
            Radio(value=" 2", label="2", tooltip="2 часа пропуска"),
            Radio(value="1y", label="1y", tooltip="1 час (уважительно)"),
            Radio(value="2y", label="2y", tooltip="2 часа (уважительно)"),
            Radio(value=" .", label="Пусто", tooltip="Очистить поле")
        ]))

        self.text_date = Text("")
        self.dlg = AlertDialog(
            title=self.text_date,
            content=Row(
                controls=[
                    self.radio_group
                ]
            ),
            actions=[
                TextButton("Сохранить", on_click=lambda e: self.show_window_save(e)),
                TextButton("Отмена", on_click=lambda e: self.show_window_cancel(e))

            ],
        )

    def update_table(self):
        self.columns_table_lecture = [DataColumn(Text(f"{self.week_list[i]}", color="black")) for i in range(7)]
        self.row_table_lecture = [  # i - строки | j - столбцы
            DataRow([
                DataCell(
                    Container(
                        content=Text(f"{self.list_name[i]}" if j == 0 else f"    {self.statement.check_which_value(
                            self.db.get_info_join(f"{self.list_name[i]}", f"{self.date_lecture[j - 1]}",
                                                  f"{self.value}", "lecture"))}",
                                     size=25, color="black"),
                        width=200 if j == 0 else None,
                        on_click=lambda e, n=j, a=i:
                        self.put_grade_student(self.date_lecture[n - 1], self.list_name[a])
                        if n != 0 else None,
                    )
                )
                for j in range(7)
            ])
            for i in range(len(self.list_name))
        ]
        self.scroll_table_lecture.controls.clear()
        # Добавляем обновленную таблицу
        self.scroll_table_lecture.controls.append(DataTable(
            width=800,
            bgcolor="white",
            border=border.all(2, "#00FF7F"),
            border_radius=5,
            vertical_lines=BorderSide(2, "black"),
            columns=self.columns_table_lecture,
            rows=self.row_table_lecture,
        )
        )
        self.page.update()

# окно при нажатии на оценку
    def put_grade_student(self, date, name):
        if date == "                 ":
            self.page.show_banner(self.banner)
        else:
            value_t = self.statement.check_which_value(self.db.get_info_join(f"{name}", f"{date}",
                                                                         f"{self.value}", "lecture"))
            self.text_date.value = f"{name} | {date}"
            self.radio_group.value = value_t  # значение для radio button
            self.page.show_banner(self.dlg)

    def show_window_cancel(self, e):
        self.page.show_banner(self.cancel)

    def show_window_save(self, e):
        name, date = self.text_date.value.split(" | ")  # отделяем имя, дату
        self.db.delete_info_statement(f"{name}", f"{date}", f"{self.value}", f"lecture")
        if self.radio_group.value != " .":
            self.db.insert_info_values(f"statement_lecture{self.value}", f"'{name}', '{date}', "
                                                                         f"'{self.radio_group.value}'")
        self.page.show_banner(self.save)
        self.update_table()

    def add_date_lecture(self, e):
        self.page.show_banner(
            DatePicker(
                first_date=datetime.datetime(year=2024, month=9, day=1),
                last_date=datetime.datetime(year=self.now.year, month=self.now.month, day=self.now.day),
                on_change=lambda e: self.add_lecture(e),
            )
        ),

    def add_lecture(self, e):
        if e.control.value.strftime('%d.%m.%Y') in self.date_lecture:
            self.page.show_banner(self.error_date)
        else:
            self.db.insert_info_values(f"date_{self.value}",
                                   f"'{e.control.value.strftime('%d.%m.%Y')}', 'lecture', 'None'")


class TableConsultation(TableLecture):
    def __init__(self, pageN, id, db, value, today_date):
        super().__init__(pageN, id, db, value, today_date)
        self.page.vertical_alignment = MainAxisAlignment.CENTER

        self.scroll_table_consultation = ListView(expand=1, spacing=10, padding=15, width=1200, visible=False)

        self.but_add_consultation = IconButton(icons.ADD_BOX,
                                    icon_size=35,
                                    tooltip="Добавить дату",
                                    icon_color="#3056FF",
                                    on_click=lambda e: self.add_date_consultation(e),
                                    )

        self.but_date_consultation = IconButton(icons.DATE_RANGE_ROUNDED,
                                     icon_size=35,
                                     tooltip="Изменить даты",
                                     icon_color="#3056FF",
                                     )

# Таблица с датами КОНСУЛЬТАЦИЯ
        self.column_table_consultation_date = [DataColumn(Text(f"{self.date_consultation[i]}", color="black", size=18)) for i in range(6)]

        self.table_consultation_date = DataTable(
            width=875,
            bgcolor="white",
            border=border.all(2, "#061CF9"),
            border_radius=5,
            vertical_lines=BorderSide(2, "black"),
            columns=self.column_table_consultation_date,
        )
        self.container_table_consultation_date = Container(
            Row([
                self.but_date_consultation,
                self.but_add_consultation,
                self.table_consultation_date
            ], alignment=MainAxisAlignment.CENTER),
            padding=padding.only(left=180),
            visible=False
        )

# таблица основная КОНСУЛЬТАЦИЯ
        self.column_consultation = [DataColumn(Text(f"{self.week_list[i]}", color="black")) for i in range(7)]
        self.rows_consultation = [  # i - строки | j - столбцы
            DataRow([
                DataCell(
                    Container(
                        content=Text(f"{self.list_name[i]}" if j == 0 else f"    {self.statement.check_which_value(
                            self.db.get_info_join(f"{self.list_name[i]}", f"{self.date_consultation[j - 1]}",
                                                  f"{self.value}", "consultation"))}",
                                     size=25, color="black"),
                        width=200 if j == 0 else None,
                        on_click=lambda e, n=j, a=i:
                        self.put_grade_student_consultation(self.date_consultation[n-1], self.list_name[a])
                        if n != 0 else None,
                    )
                )
                for j in range(7)
            ])
            for i in range(len(self.list_name))
        ]

        table_consultation = DataTable(
            width=800,
            bgcolor="white",
            border=border.all(2, "#061CF9"),
            border_radius=5,
            vertical_lines=BorderSide(2, "black"),
            columns=self.column_consultation,
            rows=self.rows_consultation,
        )

        self.scroll_table_consultation.controls.append(table_consultation)

# radio button
        self.radio_group_consultation = RadioGroup(content=Row([
            Radio(value=" 1", label="1", tooltip="1 час пропуска"),
            Radio(value=" 2", label="2", tooltip="2 часа пропуска"),
            Radio(value="1y", label="1y", tooltip="1 час (уважительно)"),
            Radio(value="2y", label="2y", tooltip="2 часа (уважительно)"),
            Radio(value=" .", label="Пусто", tooltip="Очистить поле")
        ]))

        self.text_date_consultation = Text("")
        self.dlg_consultation = AlertDialog(
            title=self.text_date_consultation,
            content=Row(
                controls=[
                    self.radio_group_consultation
                ]
            ),
            actions=[
                TextButton("Сохранить", on_click=lambda e: self.show_window_save_consultation(e)),
                TextButton("Отмена", on_click=lambda e: self.show_window_cancel_consultation(e))

            ],
        )

    def update_table_consultation(self):
        self.column_consultation = [DataColumn(Text(f"{self.week_list[i]}", color="black")) for i in range(7)]
        self.rows_consultation = [  # i - строки | j - столбцы
            DataRow([
                DataCell(
                    Container(
                        content=Text(f"{self.list_name[i]}" if j == 0 else f"    {self.statement.check_which_value(
                            self.db.get_info_join(f"{self.list_name[i]}", f"{self.date_consultation[j - 1]}", 
                                                  f"{self.value}",  "consultation"))}",
                                     size=25, color="black"),
                        width=200 if j == 0 else None,
                        on_click=lambda e, n=j, a=i:
                        self.put_grade_student_consultation(self.date_consultation[n - 1], self.list_name[a])
                        if n != 0 else None,
                    )
                )
                for j in range(7)
            ])
            for i in range(len(self.list_name))
        ]
        self.scroll_table_consultation.controls.clear()
        # Добавляем обновленную таблицу
        self.scroll_table_consultation.controls.append(DataTable(
            width=800,
            bgcolor="white",
            border=border.all(2, "#061CF9"),
            border_radius=5,
            vertical_lines=BorderSide(2, "black"),
            columns=self.column_consultation,
            rows=self.rows_consultation,
        )
        )
        self.page.update()

# окно при нажатии на оценку
    def put_grade_student_consultation(self, date, name):
        if date == "                 ":
            self.page.show_banner(self.banner)
        else:
            value_t = self.statement.check_which_value(self.db.get_info_join(f"{name}", f"{date}",
                                                                         f"{self.value}", "consultation"))
            self.text_date_consultation.value = f"{name} | {date}"
            self.radio_group_consultation.value = value_t  # значение для radio button
            self.page.show_banner(self.dlg_consultation)

    def show_window_cancel_consultation(self, e):
        self.page.show_banner(self.cancel)

    def show_window_save_consultation(self, e):
        name, date = self.text_date_consultation.value.split(" | ")  # отделяем имя, дату
        self.db.delete_info_statement(f"{name}", f"{date}", f"{self.value}", f"consultation")
        if self.radio_group_consultation.value != " .":
            self.db.insert_info_values(f"statement_consultation{self.value}", f"'{name}', '{date}', "
                                                                         f"'{self.radio_group_consultation.value}'")
        self.page.show_banner(self.save)
        self.update_table_consultation()

    def add_date_consultation(self, e):
        self.page.show_banner(
            DatePicker(
                first_date=datetime.datetime(year=2024, month=9, day=1),
                last_date=datetime.datetime(year=self.now.year, month=self.now.month, day=self.now.day),
                on_change=lambda e: self.add_consultation(e),
            )
        ),

    def add_consultation(self, e):
        if e.control.value.strftime('%d.%m.%Y') in self.date_consultation:
            self.page.show_banner(self.error_date)
        else:
            self.db.insert_info_values(f"date_{self.value}",
                                   f"'{e.control.value.strftime('%d.%m.%Y')}', 'consultation', 'None'")


class TablePractice(TableConsultation):
    def __init__(self, pageN, id, db, value, today_date):
        super().__init__(pageN, id, db, value, today_date)
        self.page.vertical_alignment = MainAxisAlignment.CENTER

        self.text_group_1 = Text("Подгруппа 1", size=30)
        self.text_group_2 = Text("Подгруппа 2", size=30)

        self.but_add_1 = IconButton(icons.ADD_BOX,
                                    icon_size=35,
                                    tooltip="Добавить дату",
                                    on_click=lambda e: self.add_date_1(e)
                                    )
        self.but_add_2 = IconButton(icons.ADD_BOX,
                                    icon_size=35,
                                    icon_color="#B26CF9",
                                    tooltip="Добавить дату",
                                    on_click=lambda e: self.add_date_2(e)
                                    )
        self.but_date_1 = IconButton(icons.DATE_RANGE_ROUNDED,
                                     icon_size=35,
                                     tooltip="Изменить даты"
                                     )
        self.but_date_2 = IconButton(icons.DATE_RANGE_ROUNDED,
                                     icon_size=35,
                                     icon_color="#B26CF9",
                                     tooltip="Изменить даты"
                                     )
        self.but_edit = ElevatedButton(text="Изменить список подгрупп",
                                       icon=icons.ARTICLE_SHARP,
                                       width=300,
                                       on_click=lambda e: self.edit_group_student(e)
                                       )

        self.container_1 = Container(
            Row([
                self.text_group_1,
                self.but_add_1,
                self.but_date_1,
            ])
        )

        self.container_2 = Container(
            Row([
                self.text_group_2,
                self.but_add_2,
                self.but_date_2,
            ])
        )

        self.scroll_table_practice = ListView(expand=1, spacing=10, padding=15, width=1200, visible=False)

        self.list_subgroup_1 = self.teacher.get_list_name(
            self.db.get_info_select_from_where("name", f"group{self.value}", "subgroup", "1")
        )
        self.list_subgroup_2 = self.teacher.get_list_name(
            self.db.get_info_select_from_where("name", f"group{self.value}", "subgroup", "2")
        )
        self.list_subgroup_3 = self.teacher.get_list_name(
            self.db.get_info_select_from_where("name", f"group{self.value}", "subgroup", "None")
        )

# таблица 1
        self.column_practice = [DataColumn(Text("Имя" if i == 0 else f"{self.date_practice_1[i-1]}", color="black", size=20)) for i in range(7)]

        self.rows_practice = [  # i - строки | j - столбцы
            DataRow([
                DataCell(
                    Container(
                        content=Text(f"{self.list_subgroup_1[i]}" if j == 0 else f"{self.statement.check_which_value_practice(
                            self.db.get_info_select_from("subgroup, value", f"statement_practice{self.value} WHERE "
                                                                            f"name='{self.list_subgroup_1[i]}'"
                                                                            f" AND date='{self.date_practice_1[j-1]}'"
                                                         ))}",
                                     size=25, color="black"),
                        width=200 if j == 0 else None,
                        on_click=lambda e, n=j, a=i:
                        self.put_grade_student_practice(self.date_practice_1[n-1], self.list_subgroup_1[a])
                        if n != 0 else None,
                    ),
                )
                for j in range(7)
            ])
            for i in range(len(self.list_subgroup_1))
        ]

        table_practice_1 = DataTable(
            width=800,
            bgcolor="white",
            border=border.all(2, "#F90606"),
            border_radius=5,
            vertical_lines=BorderSide(2, "black"),
            columns=self.column_practice,
            rows=self.rows_practice,
        )

# таблица 2
        self.column_practice = [DataColumn(Text("Имя" if i == 0 else f"{self.date_practice_2[i-1]}", color="black", size=20)) for i in range(7)]
        self.rows_practice = [  # i - строки | j - столбцы
            DataRow([
                DataCell(
                    Container(
                        content=Text(f"{self.list_subgroup_2[i]}" if j == 0 else f"{self.statement.check_which_value_practice(
                            self.db.get_info_select_from("subgroup, value", f"statement_practice{self.value} WHERE "
                                                                            f"name='{self.list_subgroup_2[i]}'"
                                                                            f" AND date='{self.date_practice_2[j-1]}'"
                                                         ))}",
                                     size=25, color="black"),
                        width=200 if j == 0 else None,
                        on_click=lambda e, n=j, a=i:
                        self.put_grade_student_practice(self.date_practice_2[n - 1], self.list_subgroup_2[a])
                        if n != 0 else None,
                    )
                )
                for j in range(7)
            ])
            for i in range(len(self.list_subgroup_2))
        ]

        table_practice_2 = DataTable(
            width=800,
            bgcolor="white",
            border=border.all(2, "#F90606"),
            border_radius=5,
            vertical_lines=BorderSide(2, "black"),
            columns=self.column_practice,
            rows=self.rows_practice,
        )
        self.scroll_table_practice.controls.append(self.container_1)
        self.scroll_table_practice.controls.append(table_practice_1)
        self.scroll_table_practice.controls.append(self.but_edit)
        self.scroll_table_practice.controls.append(self.container_2)
        self.scroll_table_practice.controls.append(table_practice_2)

# radio button
        self.radio_group_practice = RadioGroup(content=Container(
            Column([
                Text("Посещаемость:", size=20),
                Row([
                    Radio(value=" 1", label="1", tooltip="1 час пропуска"),
                    Radio(value=" 2", label="2", tooltip="2 часа пропуска"),
                    Radio(value="1y", label="1y", tooltip="1 час (уважительно)"),
                    Radio(value="2y", label="2y", tooltip="2 часа (уважительно)"),
                    Radio(value=" .", label="Пусто", tooltip="Очистить поле")
                ])
            ]),
            bgcolor="#FE8A85",
            padding=10,
            border_radius=10
        ))

        self.radio_group_practice_grade = RadioGroup(content=Container(
            Column([
                Text("Оценка:", size=20),
                Row([
                    Radio(value=" 1", label="1"),
                    Radio(value=" 2", label="2"),
                    Radio(value=" 3", label="3"),
                    Radio(value=" 4", label="4"),
                    Radio(value=" 5", label="5"),
                ]),
                Row([
                    Radio(value=" 6", label="6"),
                    Radio(value=" 7", label="7"),
                    Radio(value=" 8", label="8"),
                    Radio(value=" 9", label="9"),
                    Radio(value="10", label="10"),
                ]),
                Radio(value=" .", label="Пусто")
            ]),
            bgcolor="#FE8A85",
            padding=10,
            border_radius=10
        ))

        self.text_date_practice = Text("")
        self.dlg_practice = AlertDialog(
            title=self.text_date_practice,
            content=Column(
                controls=[
                    self.radio_group_practice,
                    self.radio_group_practice_grade
                ], height=270
            ),
            actions=[
                TextButton("Сохранить", on_click=lambda e: self.show_window_save_practice(e)),
                TextButton("Отмена", on_click=lambda e: self.show_window_cancel_practice(e))

            ],
        )

    def update_table_practice(self):
        pass

# окно при нажатии на оценку
    def put_grade_student_practice(self, date, name):
        if date == "                 ":
            self.page.show_banner(self.banner)
        else:
            value_t = self.statement.check_which_value(self.db.get_info_join(f"{name}", f"{date}",
                                                                         f"{self.value}", "practice"))
            value_g = self.statement.check_which_value(self.db.get_info_select_from("subgroup",
                                                                                    f"statement_practice{self.value} "
                                                                                    f"WHERE name='{name}' "
                                                                                    f"AND date='{date}'"))
            self.text_date_practice.value = f"{name} | {date}"
            self.radio_group_practice.value = value_t  # значение для radio button
            self.radio_group_practice_grade.value = value_g
            self.page.show_banner(self.dlg_practice)

    def show_window_cancel_practice(self, e):
        self.page.show_banner(self.cancel)

    def show_window_save_practice(self, e):
        name, date = self.text_date_practice.value.split(" | ")  # отделяем имя, дату
        self.db.delete_info_statement(f"{name}", f"{date}", f"{self.value}", f"practice")
        if self.radio_group_practice.value != " ." or self.radio_group_practice_grade.value != " .":
            self.db.insert_info_values(f"statement_practice{self.value}", f"'{name}', '{date}', "
                                                                          f"'{self.radio_group_practice.value}', "
                                                                          f"'{self.radio_group_practice_grade.value}'")
        self.page.show_banner(self.save)
        self.update_table_practice()

    def edit_group_student(self, e):
        self.page.clean()
        Subgroup(self.page, self.id, self.db, self.value, self.date)

    def add_date_1(self, e):
        self.page.show_banner(
            DatePicker(
                first_date=datetime.datetime(year=2024, month=9, day=1),
                last_date=datetime.datetime(year=self.now.year, month=self.now.month, day=self.now.day),
                on_change=lambda e: self.handle_change_1(e),
            )
        ),

    def handle_change_1(self, e):
        if e.control.value.strftime('%d.%m.%Y') in self.date_practice_1:
            self.page.show_banner(self.error_date)
        else:
            self.db.insert_info_values(f"date_{self.value}",
                                   f"'{e.control.value.strftime('%d.%m.%Y')}', 'practice', '1'")

    def add_date_2(self, e):
        self.page.show_banner(
            DatePicker(
                first_date=datetime.datetime(year=2024, month=9, day=1),
                last_date=datetime.datetime(year=self.now.year, month=self.now.month, day=self.now.day),
                on_change=lambda e: self.handle_change_2(e),
            )
        ),

    def handle_change_2(self, e):
        if e.control.value.strftime('%d.%m.%Y') in self.date_practice_2:
            self.page.show_banner(self.error_date)
        else:
            self.db.insert_info_values(f"date_{self.value}",
                                   f"'{e.control.value.strftime('%d.%m.%Y')}', 'practice', '2'")


class Visible(TablePractice):
    def __init__(self, pageN, id, db, value, today_date):
        super().__init__(pageN, id, db, value, today_date)

        self.choice_mini = Container(
            CupertinoSegmentedButton(
                selected_index=1,
                selected_color=colors.RED_400,
                on_change=self.choice_table,
                controls=[
                    Text("ПРАКТИКА", size=18),
                    Container(
                        padding=padding.symmetric(0, 30),
                        content=Text("ЛЕКЦИЯ", size=18),
                    ),
                    Container(
                        padding=padding.symmetric(0, 10),
                        content=Text("КОНСУЛЬТАЦИЯ", size=18),
                    ),
                ],
            ),
        )

# CupertinoSlidingSegmentedButton
        self.page.add(
            Row(
                [
                    IconButton(icons.ARROW_BACK, on_click=self.click_arrow),
                    CupertinoSlidingSegmentedButton(
                        selected_index=1,
                        thumb_color=colors.BLUE_400,
                        padding=padding.symmetric(0, 15),
                        controls=[
                            Text("КАРТОЧКИ", size=25),
                            Text("ТАБЛИЦА", size=25),
                            Text("ОТПРАВИТЬ", size=25),
                        ],
                        on_change=self.on_segment_change,
                    ),
                ], alignment=MainAxisAlignment.CENTER,
            ),
        )

# Отрисовка Card
        self.page.add(self.scroll_card)
        self.page.add(
            Row(
                [
                    Row([
                        self.add_student_but,
                        self.add_file_but,
                    ])
                ], alignment=MainAxisAlignment.CENTER
            )
        )

# Отрисовка Table
        self.page.add(
            self.container_table_lecture_date,
            self.container_table_consultation_date,
            self.scroll_table_lecture,
            self.scroll_table_consultation,
            self.scroll_table_practice,
        )
        self.page.add(self.choice_mini)

# Видимость областей мини
    def choice_table(self, e):
        selected_index = e.control.selected_index
        if selected_index == 0:
            self.scroll_table_practice.visible = True

            self.scroll_table_lecture.visible = False
            self.scroll_table_consultation.visible = False

            self.container_table_lecture_date.visible = False
            self.container_table_consultation_date.visible = False
        elif selected_index == 1:
            self.scroll_table_lecture.visible = True
            self.container_table_lecture_date.visible = True

            self.scroll_table_practice.visible = False
            self.scroll_table_consultation.visible = False

            self.container_table_consultation_date.visible = False
        else:
            self.scroll_table_consultation.visible = True
            self.container_table_consultation_date.visible = True

            self.scroll_table_lecture.visible = False
            self.scroll_table_practice.visible = False

            self.container_table_lecture_date.visible = False
        self.page.update()

# Видимость областей
    def on_segment_change(self, e):
        if e.control.selected_index == 0:  # Cards
            self.scroll_table_practice.visible = False
            self.scroll_table_lecture.visible = False
            self.scroll_table_consultation.visible = False
            self.container_table_lecture_date.visible = False
            self.container_table_consultation_date.visible = False

            self.scroll_card.visible = True
            self.scroll_table_lecture.visible = False
            self.add_student_but.visible = True
            self.add_file_but.visible = True

            self.choice_mini.visible = False

        elif e.control.selected_index == 1:  # Table
            self.scroll_card.visible = False
            self.add_student_but.visible = False
            self.add_file_but.visible = False
            self.choice_mini.visible = True
            self.choice_table(e)
        else:
            self.scroll_table_practice.visible = False
            self.scroll_table_lecture.visible = False
            self.scroll_table_consultation.visible = False
            self.container_table_lecture_date.visible = False
            self.container_table_consultation_date.visible = False

            self.choice_mini.visible = False
            self.scroll_card.visible = False
            self.add_file_but.visible = False
            self.scroll_table_lecture.visible = False
            self.add_student_but.visible = False
        self.page.update()

# стрелка назад
    def click_arrow(self, e):
        self.page.clean()
        Numbers(self.page, self.id, self.db)


class Subgroup(Visible):
    def __init__(self, pageN, id, db, value, today_date):
        super().__init__(pageN, id, db, value, today_date)
        self.page.clean()

        self.radio_groups = []  # Список для хранения всех радио-групп

        def add_containers(list_subgroup, bg_color, radio_value):
            rows = []
            current_row = []

            for i, name in enumerate(list_subgroup):
                radio_group = RadioGroup(
                    value=radio_value,  # Устанавливаем начальное значение
                    content=Row([
                        Radio(value="1", label="1"),
                        Radio(value="2", label="2"),
                        Radio(value="None", label="Ничего"),
                    ])
                )
                self.radio_groups.append((name, radio_group))

                container = Container(
                    content=Column([
                        Text(name, size=30),
                        Column([
                            Text("Номер подгруппы:", size=15),
                            radio_group
                        ])
                    ], alignment=MainAxisAlignment.CENTER, spacing=20),
                    bgcolor=bg_color,
                    width=260,
                    padding=10,
                    border_radius=10
                )

                current_row.append(container)

                if len(current_row) == 7 or i == len(list_subgroup) - 1:
                    rows.append(Row(current_row))
                    current_row = []

            for row in rows:
                self.page.add(row)

        # Заполнение подгрупп
        add_containers(self.list_subgroup_1, "#F96D3C", "1")
        self.page.add(Row([]))
        add_containers(self.list_subgroup_2, "#FF0000", "2")
        self.page.add(Row([]))
        add_containers(self.list_subgroup_3, "#00FF00", "None")

        self.but_save = ElevatedButton(
            content=Text("Сохранить", size=15),
            width=150,
            height=50,
            bgcolor="#9FE6EE",
            on_click=self.save_data
        )
        self.but_back = ElevatedButton(
            content=Text("Назад", size=15),
            width=150,
            height=50,
            bgcolor="#9FE6EE",
            on_click=self.go_back
        )
        self.page.add(
            Row([
                self.but_back,
                self.but_save
            ], alignment=MainAxisAlignment.CENTER)
        )

        self.page.update()

    def save_data(self, e):
        for name, radio_group in self.radio_groups:
            selected_value = radio_group.value
            self.db.set_info_update(f"group{self.value}", f"subgroup='{selected_value}'", f"name='{name}'")
        Subgroup(self.page, self.id, self.db, self.value, self.date)

    def go_back(self, e):
        self.page.clean()
        Visible(self.page, self.id, self.db, self.value, self.date)


class Admin:
    def __init__(self, pageA, dbA):
        self.page = pageA
        self.db = dbA
        self.page.clean()
        self.page.update()

        self.admin = Admins()
        self.statement = Statement()

        self.page.horizontal_alignment = CrossAxisAlignment.CENTER
        self.page.vertical_alignment = MainAxisAlignment.CENTER
        self.teachers_lv = ListView(expand=1, spacing=10, padding=20, width=1000)
        self.students_lv = ListView(expand=1, spacing=10, padding=20, visible=False, width=500)

# кнопки добавление
        self.floating_action_button_teachers = FloatingActionButton(icon=icons.ADD, on_click=self.fab_pressed_teachers,
                                                                    bgcolor=colors.LIME_300)

        self.floating_action_button_students = FloatingActionButton(icon=icons.ADD, on_click=self.fab_pressed_students,
                                                                    bgcolor=colors.LIME_300, visible=False)
        self.page.add(self.floating_action_button_teachers, self.floating_action_button_students)

# CupertinoSlidingSegmentedButton
        self.page.add(
            Row(
                [
                    CupertinoSlidingSegmentedButton(
                        selected_index=0,
                        thumb_color=colors.BLUE_400,
                        padding=padding.symmetric(0, 15),
                        controls=[
                            Text("ПРЕПОДАВАТЕЛИ", size=25),
                            Text("УЧЕНИКИ", size=25),
                        ],
                        on_change=self.on_segment_change,
                    ),
                ], alignment=MainAxisAlignment.CENTER,
            )
        )

# преподаватели card
        self.list_teachers = self.admin.get_list(self.db.get_info_select_from("name", "teachers"))
        self.len_list_teachers = len(self.list_teachers)

        for i in range(self.len_list_teachers - 1):
            card_container = Container(
                content=Column(
                    [
                        ListTile(
                            title=Text(f"{self.list_teachers[i + 1]}", size=40),
                            leading=Icon(icons.ACCOUNT_BOX, size=50),
                            trailing=PopupMenuButton(
                                icon=icons.MORE_VERT,
                                items=[
                                    PopupMenuItem(text="Аккаунт",
                                                  on_click=lambda _, name=self.list_teachers[i + 1]:
                                                  self.transition_account(name)),
                                    PopupMenuItem(text="Изменить",
                                                  on_click=lambda _, name=self.list_teachers[i + 1]:
                                                  self.transition_edit(name)),
                                    PopupMenuItem(text="Удалить",
                                                  on_click=lambda _, name=self.list_teachers[i + 1]:
                                                  self.delete_teacher("teachers", f"name='{name}'")),
                                ],
                                icon_size=35
                            ),
                        ),
                    ]
                ),
                width=600,
                padding=10,
                bgcolor=colors.SURFACE_VARIANT,
                border_radius=border_radius.all(15)
            )
            self.teachers_lv.controls.append(card_container)
            self.page.add(self.teachers_lv)
            self.page.add(self.students_lv)

# ученики card
        self.list_num_group = self.admin.get_list(self.db.get_info_select_from("num_group", "group_db"))

        len_list_num_group = len(self.list_num_group)
        for i in range(len_list_num_group):
            card_container_student = Container(
                content=Column(
                    [
                        ListTile(
                            title=Text(f"{self.list_num_group[i]}", size=70),
                            trailing=PopupMenuButton(
                                icon=icons.MORE_VERT,
                                items=[
                                    PopupMenuItem(text="Список",
                                                  on_click=lambda _, number=self.list_num_group[i]:
                                                  self.transition_list(number)),
                                    PopupMenuItem(text="Изменить",
                                                  on_click=lambda _, number=self.list_num_group[i]:
                                                  self.transition_edit_group(number)),
                                    PopupMenuItem(text="Удалить",
                                                  on_click=lambda _, number=self.list_num_group[i]:
                                                  self.delete_table(number))
                                ],
                                icon_size=35
                            ),
                        ),
                    ]
                ),
                width=600,
                padding=10,
                bgcolor=colors.SURFACE_VARIANT,
                border_radius=border_radius.all(15)
            )
            self.students_lv.controls.append(card_container_student)

# кнопка плюсик
    def fab_pressed_students(self, e):
        self.page.clean()
        AddGroup(self.page, self.db)

    def fab_pressed_teachers(self, e):
        self.page.clean()
        AddTeachers(self.page, self.db)

# видимость
    def on_segment_change(self, e):
        if e.control.selected_index == 0:
            self.teachers_lv.visible = True
            self.students_lv.visible = False
            self.floating_action_button_teachers.visible = True
            self.floating_action_button_students.visible = False
        else:
            self.teachers_lv.visible = False
            self.students_lv.visible = True
            self.floating_action_button_students.visible = True
            self.floating_action_button_teachers.visible = False
        self.page.update()

# пункты
    def delete_table(self, number):
        self.db.drop_table(number)
        Admin(self.page, self.db)

    def delete_teacher(self, table, condition):
        self.db.delete_teachers(table, condition)
        Admin(self.page, self.db)

    def transition_account(self, name):
        self.page.clean()
        AccountTeachers(self.page, name, 1, self.db)

    def transition_edit(self, name):
        self.page.clean()
        EditTeachers(self.page, self.db, name)

    def transition_list(self, number):
        self.page.clean()
        AdminGroup(self.page, self.db, number)

    def transition_edit_group(self, number):
        self.page.clean()
        EditGroup(self.page, self.db, number)


class AdminGroup(Admin):
    def __init__(self, pageA, dbA, number):
        super().__init__(pageA, dbA)
        self.page.clean()
        self.page.update()
        self.group = number
        self.page.horizontal_alignment = CrossAxisAlignment.CENTER
        self.page.vertical_alignment = MainAxisAlignment.CENTER
        self.lv = ListView(expand=1, spacing=10, padding=20, width=700)

# стрелка назад
        self.page.add(
            Row(
                [
                    IconButton(icons.ARROW_BACK, on_click=self.click_arrow),
                ],
                alignment=MainAxisAlignment.START,
            )
        )

# контейнер
        self.list_name = self.admin.get_list(self.db.get_info_select_from("name", f"group{self.group}"))
        len_list_name = len(self.list_name)
        for i in range(len_list_name):
            card_container = Container(
                content=Column(
                    [
                        ListTile(
                            title=Text(f"{self.list_name[i]}", size=40),
                            leading=Icon(icons.ACCOUNT_BOX, size=50),
                            trailing=PopupMenuButton(
                                icon=icons.MORE_VERT,
                                items=[
                                    PopupMenuItem(text="Аккаунт", on_click=lambda _, name=self.list_name[i]:
                                    print(name)),
                                    PopupMenuItem(text="Изменить",
                                                  on_click=lambda _, name=self.list_name[i]:
                                                  self.transition_class_edit(name)),
                                    PopupMenuItem(text="Удалить",
                                                  on_click=lambda _, name=self.list_name[i]:
                                                  self.delete_student(f"{self.group}", f"name='{name}'"))
                                ],
                                icon_size=35
                            ),
                        ),
                    ]
                ),
                width=600,
                padding=10,
                bgcolor=colors.SURFACE_VARIANT,
                border_radius=border_radius.all(15)
            )
            self.lv.controls.append(card_container)

        self.page.add(self.lv)

# кнопки для КАРТОЧКИ
        self.add_student_but = ElevatedButton(text="Добавить студента", width=300, height=50,
                                              bgcolor='#B0E0E6', color='black', on_click=self.add_student)
        self.add_file_but = ElevatedButton(text="Добавить данные через Excel", width=300, height=50,
                                           bgcolor='#B0E0E6', color='black', on_click=self.add_file)
        self.page.add(
            Row(
                [
                    Row([
                        self.add_student_but,
                        self.add_file_but,
                    ])
                ], alignment=MainAxisAlignment.CENTER
            )
        )

    def delete_student(self, group, condition):
        self.db.delete_student(group, condition)
        AdminGroup(self.page, self.db, self.group)

    def add_student(self, e):
        self.page.clean()
        AddStudent(self.page, self.db, self.group, 1, )

    def add_file(self, e):
        self.page.clean()
        ExcelFile(self.page, self.db, 1, self.group)

    def click_arrow(self, e):
        self.page.clean()
        Admin(self.page, self.db)
        self.page.update()

    def transition_class_edit(self, name):
        self.page.clean()
        EditStudent(self.page, self.db, name, self.group, 1)
        self.page.update()


class AccountTeachers(Admin):
    def __init__(self, pageA, name, id, dbA):
        super().__init__(pageA, dbA)
        self.page.clean()
        self.page.update()
        self.id = id
        self.name = name
        self.page.horizontal_alignment = CrossAxisAlignment.CENTER
        self.page.vertical_alignment = MainAxisAlignment.START

        self.page.add(
            Row(
                [
                    IconButton(icons.ARROW_BACK, on_click=self.click_arrow),
                ],
                alignment=MainAxisAlignment.START,
            )
        )
        self.page.add(
            Row(
                [
                    Text(f"{name}", size=50)
                ],
                alignment=MainAxisAlignment.CENTER,
            )
        )

# Номера в список
        self.cl_list_number = self.admin.get_list(self.db.get_info_select_from_where("num_group", "teachers",
                                                                                     "name", name))
# Предметы в список
        self.cl_list_item = self.admin.get_list(self.db.get_info_select_from_where("items", "teachers",
                                                                                   "name", name))
# ExpansionTile
        self.page.add(
            ExpansionTile(
                title=Text("Предметы", size=40, color="black"),
                controls=[ListTile(title=Text(f"{self.cl_list_item[0]}", color='black', size=30))],
                width=700,
                bgcolor="#AFEEEE",
                collapsed_bgcolor="#AED6F1",

            ),
            ExpansionTile(
                title=Text("Группы", size=40, color="black"),
                controls=[ListTile(title=Text(f"{self.cl_list_number[0]}", color='black', size=30))],
                width=700,
                bgcolor="#AFEEEE",
                collapsed_bgcolor="#AED6F1",
            ),
        )

    def click_arrow(self, e):
        self.page.clean()
        if self.id == 1:
            Admin(self.page, self.db)
        else:
            Numbers(self.page, self.id, self.db)
        self.page.update()


class SettingsAdmin(Admin):
    def __init__(self, pageA, dbA, id):
        super().__init__(pageA, dbA)
        self.page.clean()
        self.page.update()
        self.id = id

        list_str = self.admin.get_list(self.db.get_info_select_from_where("name, password, email",
                                                                          "teachers", "rowid", id))
        self.name_db = str(list_str[0])
        self.password = str(list_str[1])
        self.email = str(list_str[2])

# виджеты
        self.t = Text("Имя и почта будут использоваться в тех.поддержке для связи с вами, для помощи", size=12)
        self.text_name = TextField(label="Имя", value=f'{self.name_db}', width=500, text_size=30,
                              border_color="#28B463", border_width=2)
        self.text_pass = TextField(label="Пароль", value=f'{self.password}', width=500, text_size=30,
                              password=True, can_reveal_password=True, border_color="#28B463", border_width=2)
        self.text_email = TextField(label="Почта", value=f'{self.email}', width=500, text_size=30,
                               border_color="#28B463", border_width=2)
        self.but_save = ElevatedButton(text="Сохранить", on_click=self.button_clicked, width=200, height=50)
        self.but_end = ElevatedButton(text="Назад", on_click=self.click_end, width=200, height=50)

# добавляем виджеты
        self.page.add(
            Column(
                [
                    self.text_email,
                    self.text_name,
                    self.text_pass,
                    self.t,
                ],
                alignment=MainAxisAlignment.CENTER,
                horizontal_alignment=CrossAxisAlignment.CENTER

            ),
            Row([
                self.but_end,
                self.but_save,
            ],
                alignment=MainAxisAlignment.CENTER,
                vertical_alignment=CrossAxisAlignment.CENTER
            )
        )

# уведомление
        self.bs = BottomSheet(
            content=Container(
                padding=50,
                content=Column(
                    tight=True,
                    controls=[
                        Text("Нельзя,чтоб были пустые поля", size=20, color="red"),
                    ],
                ),
            ),
        )

        self.dlg = AlertDialog(
            title=Text("УСПЕШНО!", size=50, color="green"),
        )

# кнопка назад
    def click_end(self, e):
        self.page.clean()
        Admin(self.page, self.db)
        self.page.update()

# кнопка сохранить
    def button_clicked(self, e):
        if self.text_name.value == '' or self.text_pass.value == '' or self.text_email.value == '':
            self.page.show_banner(self.bs)
        else:
            self.db.set_info_update("teachers", f"name='{self.text_name.value}', "
                                                f"password='{self.text_pass.value}', "
                                                f"email='{self.text_email.value}'",
                                                f"rowid='{self.id}'")
            self.page.show_banner(self.dlg)
        self.page.update()


class EditTeachers(Admin):
    def __init__(self, pageA, dbA, name):
        super().__init__(pageA, dbA)
        self.page.clean()
        self.page.update()
        self.name = name
        self.login = ''
        self.password = ''
        self.items = ''
        self.num_group = ''

        self.list_num_group = self.admin.get_list(self.db.get_info_select_from("num_group", "group_db"))

        list_info = self.admin.get_list(self.db.get_info_select_from_where("login, password, items, num_group, rowid",
                                                                  "teachers", "name", name))
        self.login = str(list_info[0])
        self.password = str(list_info[1])
        self.items = str(list_info[2])
        self.num_group = str(list_info[3])
        self.rowid = list_info[4]

# виджеты
        self.text_name = TextField(label="Имя", value=f'{name}', width=500, text_size=30,
                                  border_color="#28B463", border_width=2)
        self.text_pass = TextField(label="Пароль", value=f'{self.password}', width=500, text_size=30,
                                  password=True, can_reveal_password=True, border_color="#28B463", border_width=2)
        self.text_login = TextField(label="Логин", value=f'{self.login}', width=500, text_size=30,
                                   border_color="#28B463", border_width=2)
        self.text_items = TextField(label="Предметы", value=f'{self.items}', width=500, text_size=30,
                                   border_color="#28B463", border_width=2)
        self.text_num_group = TextField(label="Группы", value=f'{self.num_group}', width=500, text_size=30,
                                       border_color="#28B463", border_width=2)
        self.but_save = ElevatedButton(text="Сохранить", on_click=self.button_clicked, width=200, height=50)
        self.but_end = ElevatedButton(text="Назад", on_click=self.click_end, width=200, height=50)

# добавляем виджеты
        self.page.add(
            Column(
                    [
                        self.text_name,
                        self.text_login,
                        self.text_pass,
                        self.text_items,
                        self.text_num_group
                    ],
                    alignment=MainAxisAlignment.CENTER,
                    horizontal_alignment=CrossAxisAlignment.CENTER

                ),
                Row([
                    self.but_end,
                    self.but_save,
                ],
                    alignment=MainAxisAlignment.CENTER,
                    vertical_alignment=CrossAxisAlignment.CENTER
                )
            )

# уведомление
        self.error_write_num = Text("Нельзя,чтоб были пустые поля", size=20, color="red")
        self.bs = BottomSheet(
                content=Container(
                    padding=50,
                    content=Column(
                        tight=True,
                        controls=[
                            self.error_write_num
                        ],
                    ),
                ),
            )

        self.dlg = AlertDialog(
                title=Text("УСПЕШНО!", size=50, color="green"),
            )

        self.error = Text('', size=20, color="red")
        self.error = AlertDialog(
                title=Text("ОШИБКА", size=50, color="red"),
                content=Column(
                    tight=True,
                    controls=[
                        self.error,
                        Text("Сперва добавьте группу", size=20, color="red"),
                    ],
                ),
            )

# кнопка назад
    def click_end(self, e):
        self.page.clean()
        Admin(self.page, self.db)

# кнопка сохранить
    def button_clicked(self, e):
        if self.text_name.value == '' or self.text_pass.value == '' or self.text_login.value == '':
            self.page.show_banner(self.bs)
        elif self.text_items.value == '' or self.text_num_group.value == '':
            self.page.show_banner(self.bs)
        else:
            # проверка на правильные числа
            list_num = self.text_num_group.value.split(", ")
            kol_right = 0
            try:
                for num in list_num:
                    if int(num) not in self.list_num_group:
                        self.error.value = f'Такого номера группы ({num}) нету в базе'
                        self.page.show_banner(self.error)
                    else:
                        kol_right += 1

                if kol_right == len(list_num):
                    self.page.show_banner(self.dlg)
                    self.db.set_info_update("teachers",
                        f"name='{self.text_name.value}', "
                        f"password='{self.text_pass.value}', "
                        f"login='{self.text_login.value}', "
                        f"items='{self.text_items.value}', "
                        f"num_group='{self.text_num_group.value}'",
                        f"rowid={self.rowid}")
            except:
                self.error_write_num.value = ("ОШИБКА, в поле Группы нужно записывать через запятую и"
                                              " с одним пробелом после")
                self.page.show_banner(self.bs)
            self.page.update()


class AddGroup(Admin):
    def __init__(self, pageA, dbA):
        super().__init__(pageA, dbA)
        self.page.clean()
        self.page.update()
# виджеты
        self.text_num_group = TextField(label="Номер группы", width=500, text_size=30,
                                        border_color="#28B463", border_width=2)
        self.but_save = ElevatedButton(text="Добавить", on_click=self.button_clicked, width=200, height=50)
        self.but_end = ElevatedButton(text="Назад", on_click=self.click_end, width=200, height=50)

# добавляем виджеты
        self.page.add(
            Column(
                [
                    self.text_num_group
                ],
                alignment=MainAxisAlignment.CENTER,
                horizontal_alignment=CrossAxisAlignment.CENTER

            ),
            Row([
                self.but_end,
                self.but_save,
            ],
                alignment=MainAxisAlignment.CENTER,
                vertical_alignment=CrossAxisAlignment.CENTER
            )
        )

# уведомление
        self.bs = BottomSheet(
            content=Container(
                padding=50,
                content=Column(
                    tight=True,
                    controls=[
                        Text("Нельзя,чтоб были пустые поля", size=20, color="red"),
                    ],
                ),
            ),
        )

        self.dlg = AlertDialog(
            title=Text("УСПЕШНО!", size=50, color="green"),
        )

        self.error = AlertDialog(
            title=Text("ОШИБКА", size=50, color="red"),
            content=Column(
                tight=True,
                controls=[
                    Text("Должно быть 8 цифр", size=20, color="red"),
                ],
            ),
        )

# кнопка назад
    def click_end(self, e):
        self.page.clean()
        Admin(self.page, self.db)
        self.page.update()

# кнопка сохранить
    def button_clicked(self, e):
        try:
            if self.text_num_group.value == '':
                self.page.show_banner(self.bs)
            elif 10000000 <= int(self.text_num_group.value) <= 99999999:
                self.page.show_banner(self.dlg)
                self.db.insert_info_values("group_db", self.text_num_group.value)
                self.db.create_table_group(self.text_num_group.value)
                self.db.create_table_statement(f"{self.text_num_group.value}", "lecture")
                self.db.create_table_statement(f"{self.text_num_group.value}", "consultation")
                self.db.create_table_statement_practice(f"{self.text_num_group.value}")
                self.text_num_group.value = ''
            else:
                self.page.show_banner(self.error)
            self.page.update()
        except:
            self.page.show_banner(self.error)


class AddTeachers(Admin):
    def __init__(self, pageA, dbA):
        super().__init__(pageA, dbA)
        self.page.clean()
        self.page.update()
        self.list_num_group = self.admin.get_list(self.db.get_info_select_from("num_group", "group_db"))
# виджеты
        self.text_name = TextField(label="ФИО", width=500, text_size=30,
                                  border_color="#28B463", border_width=2)
        self.text_login = TextField(label="Логин", width=500, text_size=30,
                                   border_color="#28B463", border_width=2)
        self.text_password = TextField(label="Пароль", width=500, text_size=30,
                                      password=True, can_reveal_password=True, border_color="#28B463", border_width=2)
        self.text_items = TextField(label="Предметы", width=500, text_size=30,
                                   border_color="#28B463", border_width=2)
        self.text_num_group = TextField(label="Номер группы", width=500, text_size=30,
                                       border_color="#28B463", border_width=2)
        self.but_save = ElevatedButton(text="Добавить", on_click=self.button_clicked, width=200, height=50)
        self.but_end = ElevatedButton(text="Назад", on_click=self.click_end, width=200, height=50)

# добавляем виджеты
        self.page.add(
                Column(
                    [
                        self.text_name,
                        self.text_login,
                        self.text_password,
                        self.text_items,
                        self.text_num_group
                    ],
                    alignment=MainAxisAlignment.CENTER,
                    horizontal_alignment=CrossAxisAlignment.CENTER

                ),
                Row([
                    self.but_end,
                    self.but_save,
                ],
                    alignment=MainAxisAlignment.CENTER,
                    vertical_alignment=CrossAxisAlignment.CENTER
                )
            )

# уведомление
        self.error_write_num = Text("Нельзя,чтоб были пустые поля", size=20, color="red")
        self.bs = BottomSheet(
                content=Container(
                    padding=50,
                    content=Column(
                        tight=True,
                        controls=[
                            self.error_write_num
                        ],
                    ),
                ),
            )

        self.dlg = AlertDialog(
                title=Text("УСПЕШНО!", size=50, color="green"),
            )

        self.error_num = Text('', size=20, color="red")
        self.error = AlertDialog(
                title=Text("ОШИБКА", size=50, color="red"),
                content=Column(
                    tight=True,
                    controls=[
                        self.error_num,
                        Text("Сперва добавьте группу", size=20, color="red"),
                    ],
                ),
            )

# кнопка назад
    def click_end(self, e):
        self.page.clean()
        Admin(self.page, self.db)

# кнопка сохранить
    def button_clicked(self, e):
        if self.text_name.value == '' or self.text_password.value == '' or self.text_login.value == '':
            self.page.show_banner(self.bs)
        elif self.text_items.value == '' or self.text_num_group.value == '':
            self.page.show_banner(self.bs)
        else:
            # проверка на правильные числа
            list_num = self.text_num_group.value.split(", ")
            kol_right = 0
            try:
                for num in list_num:
                    if int(num) not in self.list_num_group:
                        self.error_num.value = f'Такого номера группы ({num}) нету в базе'
                        self.page.show_banner(self.error)
                    else:
                        kol_right += 1

                if kol_right == len(list_num):
                    self.page.show_banner(self.dlg)
                    self.db.insert_info_values("teachers", f"{self.text_name.value}, "
                                                           f"{self.text_login.value}, "
                                                           f"{self.text_password.value}, "
                                                           f"{self.text_items.value}, "
                                                           f"{self.text_num_group.value}, "
                                                           f"'None'")
                    self.text_name.value = ''
                    self.text_login.value = ''
                    self.text_password.value = ''
                    self.text_items.value = ''
                    self.text_num_group.value = ''
                    self.page.update()
            except:
                self.error_write_num.value = ("ОШИБКА, в поле Группы нужно записывать через запятую и"
                                             " с одним пробелом после")
                self.page.show_banner(self.bs)


class AddStudent(Admin):
    def __init__(self, pageA, dbA, group, id):
        super().__init__(pageA, dbA)
        self.page.clean()
        self.page.update()
        self.group = group
        self.id = id
# виджеты
        self.text_name = TextField(label="ФИО", width=500, text_size=30,
                              border_color="#28B463", border_width=2)
        self.but_save = ElevatedButton(text="Добавить", on_click=self.button_clicked, width=200, height=50)
        self.but_end = ElevatedButton(text="Назад", on_click=self.click_end, width=200, height=50)

# добавляем виджеты
        self.page.add(
            Column(
                [
                    self.text_name
                ],
                alignment=MainAxisAlignment.CENTER,
                horizontal_alignment=CrossAxisAlignment.CENTER

            ),
            Row([
                self.but_end,
                self.but_save,
            ],
                alignment=MainAxisAlignment.CENTER,
                vertical_alignment=CrossAxisAlignment.CENTER
            )
        )

# уведомление
        self.bs = BottomSheet(
            content=Container(
                padding=50,
                content=Column(
                    tight=True,
                    controls=[
                        Text("Нельзя,чтоб были пустые поля", size=20, color="red"),
                    ],
                ),
            ),
        )

        self.dlg = AlertDialog(
            title=Text("УСПЕШНО!", size=50, color="green"),
        )

        self.error = AlertDialog(
            title=Text("ОШИБКА", size=50, color="red"),
        )

# кнопка назад
    def click_end(self, e):
        self.page.clean()
        if self.id == 1:
            Admin(self.page, self.db)
        else:
            Visible(self.page, self.id, self.db, self.group, self.statement.get_today_date())
        self.page.update()

# кнопка сохранить
    def button_clicked(self, e):
        try:
            if self.text_name.value == '':
                self.page.show_banner(self.bs)
            else:
                self.page.show_banner(self.dlg)
                self.db.insert_info_values(f"group{self.group}", f"'{self.text_name.value}', 'None'")
                self.text_name.value = ''
            self.page.update()
        except:
            self.page.show_banner(self.error)


class EditGroup(Admin):
    def __init__(self, pageA, dbA, number):
        super().__init__(pageA, dbA)
        self.page.clean()
        self.page.update()
        self.number = number
        self.num_group = self.admin.get_list(self.db.get_info_select_from("num_group", "group_db"))

# виджеты
        self.text_num_group = TextField(label="Группы", value=f'{number}', width=500, text_size=30,
                                       border_color="#28B463", border_width=2)
        self.but_save = ElevatedButton(text="Сохранить", on_click=self.button_clicked, width=200, height=50)
        self.but_end = ElevatedButton(text="Назад", on_click=self.click_end, width=200, height=50)

# добавляем виджеты
        self.page.add(
            Column(
            [
                    self.text_num_group,
                    Text('Номер группы автоматически обновится у преподавателей', size=15)
                    ],
                    alignment=MainAxisAlignment.CENTER,
                    horizontal_alignment=CrossAxisAlignment.CENTER
                ),
            Row([
                self.but_end,
                self.but_save,
                ],
                    alignment=MainAxisAlignment.CENTER,
                    vertical_alignment=CrossAxisAlignment.CENTER
                )
            )

# уведомление
        self.error_write_num = Text("Нельзя,чтоб были пустые поля", size=20, color="red")
        self.bs = BottomSheet(
                content=Container(
                padding=50,
                content=Column(
                    tight=True,
                    controls=[
                        self.error_write_num
                        ],
                    ),
                ),
            )

        self.dlg = AlertDialog(
                title=Text("УСПЕШНО!", size=50, color="green"),
            )

        self.error_write = Text('Должно быть 8 цифр', size=20, color="red")
        self.error = AlertDialog(
                title=Text("ОШИБКА", size=50, color="red"),
                content=Column(
                    tight=True,
                    controls=[
                        self.error_write,
                    ],
                ),
            )

# кнопка назад
    def click_end(self, e):
        self.page.clean()
        Admin(self.page, self.db)

# кнопка сохранить
    def button_clicked(self, e):
        if self.text_num_group.value == '':
            self.page.show_banner(self.bs)
        elif self.text_num_group.value in self.num_group:
            self.error_write.value = 'Такая группа уже есть'
            self.page.show_banner(self.error)
        elif 10000000 <= int(self.text_num_group.value) <= 99999999:
            self.page.show_banner(self.dlg)
            self.db.set_info_update("group_db", f"num_group={self.text_num_group.value}", f"num_group={self.number}")
            self.db.set_alter_info_group(self.number, self.text_num_group.value)
            self.db.set_info_update_replace_like("teachers", "num_group", "num_group",
                                                 self.number, self.text_num_group.value, "num_group", self.number)
        else:
            self.page.show_banner(self.error)
        self.page.update()


class EditStudent(Admin):
    def __init__(self, pageA, dbA, name, number, id):
        super().__init__(pageA, dbA)
        self.page.clean()
        self.page.update()
        self.name = name
        self.number = number
        self.id = id

# виджеты
        self.text_name = TextField(label="ФИО", value=f'{self.name}', width=500, text_size=30,
                              border_color="#28B463", border_width=2)
        self.but_save = ElevatedButton(text="Сохранить", on_click=self.button_clicked, width=200, height=50)
        self.but_end = ElevatedButton(text="Назад", on_click=self.click_end, width=200, height=50)

# добавляем виджеты
        self.page.add(
            Column(
                [
                    self.text_name
                ],
                alignment=MainAxisAlignment.CENTER,
                horizontal_alignment=CrossAxisAlignment.CENTER

            ),
            Row([
                self.but_end,
                self.but_save,
            ],
                alignment=MainAxisAlignment.CENTER,
                vertical_alignment=CrossAxisAlignment.CENTER
            )
        )

        # уведомление
        self.error_write_num = Text("Нельзя,чтоб было пустое поле", size=20, color="red")
        self.bs = BottomSheet(
            content=Container(
                padding=50,
                content=Column(
                    tight=True,
                    controls=[
                        self.error_write_num
                    ],
                ),
            ),
        )

        self.dlg = AlertDialog(
            title=Text("УСПЕШНО!", size=50, color="green"),
        )

# кнопка назад
    def click_end(self, e):
        self.page.clean()
        if self.id == 1:
            AdminGroup(self.page, self.db, self.number)
        else:
            Visible(self.page, self.id, self.db, self.number, self.statement.get_today_date())
        self.page.update()

# кнопка сохранить
    def button_clicked(self, e):
        if self.text_name.value == '':
            self.page.show_banner(self.bs)
        else:
            self.page.show_banner(self.dlg)
            self.db.set_info_update_student(f"{self.number}", f"name='{self.text_name.value}'", f"name='{self.name}'")
        self.page.update()


class ExcelFile(Admin):
    def __init__(self, pageA, dbA, id, group):
        super().__init__(pageA, dbA)
        self.page.clean()
        self.page.update()

        self.id = id
        self.group = group

        file_picker = FilePicker()
        self.page.overlay.append(file_picker)

        self.page.add(
            ElevatedButton(text="Загрузить файл", icon=icons.FILE_OPEN, on_click=lambda _: file_picker.pick_files())
        )


def main(page: Page):
    page.theme_mode = 'light'
    Main(page)


app(target=main)