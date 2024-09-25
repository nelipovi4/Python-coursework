from flet import *
import sqlite3
import calendar
import datetime


class Main:
    def __init__(self, page, db):
        self.page = page
        self.db = db
        self.page.title = "BNTU"
        self.page.vertical_alignment = MainAxisAlignment.CENTER
        self.cursor_db = self.db.cursor()

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
        AccountTeachers(self.page, self.cursor_db, name, id, self.db)
        self.page.update()

# выход
    def logout(self):
        self.page.clean()
        Main(self.page, self.db)
        self.page.update()

# настройки
    def settings(self, id):
        self.page.clean()
        SettingsAdmin(self.page, self.cursor_db, id, self.db)
        self.page.update()

# проверка на вход
    def check_users(self, e):
        self.cursor_db.execute("SELECT rowid, login, password, name FROM teachers")
        for i in self.cursor_db:
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
                    Admin(self.page, self.cursor_db, self.db)
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
                    Numbers(self.page, self.cursor_db, i[0], self.db)


class Numbers:
    def __init__(self, page, cursor_db, id, db):
        self.page = page
        self.id = id
        self.db = db
        self.cursor_db = cursor_db
        page.vertical_alignment = MainAxisAlignment.CENTER
        page.horizontal_alignment = CrossAxisAlignment.CENTER
        self.list_num = ''
        self.create_list()
        self.click_cont()

# делаем список из номеров групп
    def create_list(self):
        self.cursor_db.execute(f"SELECT num_group FROM teachers WHERE rowid={self.id}")
        for i in self.cursor_db:
            num_group_str = i[0]
            self.list_num = num_group_str.replace(',', ' ').split()

# контейнеры и нажатие на них
    def click_cont(self):
        for i in self.list_num:
            def next_class(e, value=i):
                self.page.clean()
                self.page.update()
                Card(value, self.page, self.cursor_db, self.id, self.db)

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


class Card:
    def __init__(self, value, page, cursor_db, id, db):
        self.page = page
        self.value = value
        self.cursor_db = cursor_db
        self.id = id
        self.db = db
        self.page.vertical_alignment = MainAxisAlignment.CENTER
        self.list_motorcade = []
        self.lv = ListView(expand=1, spacing=10, padding=20,width=1000)
        self.table_lv = ListView(expand=1, spacing=10, padding=15, visible=False, width=1200)
        self.week_list = ['Имя', 'ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ']
        today = datetime.date.today()
        #print(f'{today.day - 1}/{today.month}/{today.year}')
        self.date_list = ['2/9/2024', '3/9/2024', '4/9/2024', '5/9/2024', '6/9/2024', '7/9/2024']

        self.floating_action_button = FloatingActionButton(icon=icons.ADD, on_click=self.fab_pressed,
                                                           bgcolor=colors.LIME_300)
        self.page.add(self.floating_action_button)

        # CupertinoSlidingSegmentedButton
        self.page.add(
            Row(
                [
                    IconButton(icons.ARROW_BACK, on_click=self.click_arrow),
                    CupertinoSlidingSegmentedButton(
                        selected_index=0,
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
            )
        )
# Добавляем всё в список, где есть кортежи, а затем убираем кортежи
        self.cursor_db.execute(f"SELECT name FROM group{self.value}")
        for i in self.cursor_db:
            self.list_motorcade.append(i)

        self.list_name = [x[0] for x in self.list_motorcade]
        self.len_list = len(self.list_name)
        # Контейнеры
        for i in range(self.len_list):
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
                                                  on_click=lambda _, name=self.list_name[i]: self.transition_class_edit(
                                                      name)),
                                    PopupMenuItem(text="Удалить"),
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
            self.lv.controls.append(self.card_container)
        self.page.add(self.lv)

# Таблица с датами
        self.but_calendar = ElevatedButton(text="КАЛЕНДАРЬ", width=250, height=50, bgcolor='#B0E0E6', color='black',
                                           on_click=self.transition_calendar, visible=False)
        self.columns2 = [DataColumn(Text(f"{self.date_list[i]}", color="black", size=18)) for i in range(6)]

        self.table2 = DataTable(
            width=882,
            bgcolor="white",
            border=border.all(2, "#00FF7F"),
            border_radius=5,
            vertical_lines=BorderSide(2, "black"),
            columns=self.columns2,
            visible=False
        )
        self.con = Container(
            content=self.table2,
            padding=padding.only(left=38)
        )

        self.page.add(
            Row(
                [
                    self.but_calendar,
                    self.con
                ],
                alignment=MainAxisAlignment.CENTER
            )
        )
# таблица
        self.columns = [DataColumn(Text(f"{self.week_list[i]}", color="black")) for i in range(7)]

        self.rows = [
            DataRow([
                DataCell(
                    Container(
                        content=Text(f"{self.list_name[i]}" if j == 0 else "     Н", size=25, color="black"),
                        width=200 if j == 0 else None,
                        on_click=lambda e, n=j, a=i: print(f"Столбец {n + 1}, {self.list_name[a]}") if n != 0 else None,
                    )
                )
                for j in range(7)
            ])
            for i in range(len(self.list_name))
        ]

        table = DataTable(
            width=800,
            bgcolor="white",
            border=border.all(2, "#00FF7F"),
            border_radius=5,
            vertical_lines=BorderSide(2, "black"),
            columns=self.columns,
            rows=self.rows,
        )

        self.table_lv.controls.append(table)
        self.page.add(self.table_lv)
# кнопка добавление
    def fab_pressed(self, e):
        self.page.clean()
        AddStudent(self.page, self.cursor_db, self.db, self.value, 1, id)

# Видимость областей
    def on_segment_change(self, e):
        if e.control.selected_index == 0:  # Cards
            self.lv.visible = True
            self.table_lv.visible = False
            self.floating_action_button.visible = True
            self.table2.visible = False
            self.but_calendar.visible = False
        elif e.control.selected_index == 1:  # Table
            self.lv.visible = False
            self.table_lv.visible = True
            self.floating_action_button.visible = False
            self.table2.visible = True
            self.but_calendar.visible = True
        else:  # Send
            self.lv.visible = False
            self.table_lv.visible = False
            self.floating_action_button.visible = False
            self.table2.visible = False
            self.but_calendar.visible = False
        self.page.update()

# стрелка назад
    def click_arrow(self, e):
        self.page.clean()
        Numbers(self.page, self.cursor_db, self.id, self.db)
        self.page.update()

    def transition_class_edit(self, name):
        self.page.clean()
        EditStudent(self.page, self.cursor_db, name, self.db, self.value, 1)
        self.page.update()

    def transition_calendar(self, e):
        print(1)


class Admin:
    def __init__(self, page, cursor_db, db):
        self.page = page
        self.cursor_db = cursor_db
        self.db = db
        self.page.horizontal_alignment = CrossAxisAlignment.CENTER
        self.page.vertical_alignment = MainAxisAlignment.CENTER
        self.teachers_lv = ListView(expand=1, spacing=10, padding=20, width=1000)
        self.students_lv = ListView(expand=1, spacing=10, padding=20, visible=False, width=500)
        self.list_motorcade = []

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
        self.cursor_db.execute("SELECT name FROM teachers")

        for i in self.cursor_db:
            self.list_motorcade.append(i)

        self.list_teachers = [x[0] for x in self.list_motorcade]
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
                                                  on_click=lambda _, name=self.list_teachers[i + 1]: self.transition_account(
                                                      name)),
                                    PopupMenuItem(text="Изменить",
                                                  on_click=lambda _, name=self.list_teachers[i + 1]: self.transition_edit(
                                                      name)),
                                    PopupMenuItem(text="Удалить"),
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
        self.cursor_db.execute("SELECT num_group FROM group_db")

        self.list_num_group = []

        for i in self.cursor_db:
            self.list_num_group.extend(i)

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
                                                  on_click=lambda _, number=self.list_num_group[i]: self.transition_list(number)),
                                    PopupMenuItem(text="Изменить",
                                                  on_click=lambda _, number=self.list_num_group[i]:
                                                  self.transition_edit_group(number)),
                                    PopupMenuItem(text="Удалить"),
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

    def fab_pressed_students(self, e):
        self.page.clean()
        AddGroup(self.page, self.cursor_db, self.db)
        self.page.update()

    def fab_pressed_teachers(self, e):
        self.page.clean()
        AddTeachers(self.page, self.cursor_db, self.db)
        self.page.update()

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

    def transition_account(self, name):
        self.page.clean()
        AccountTeachers(self.page, self.cursor_db, name, 1, self.db)
        self.page.update()

    def transition_edit(self, name):
        self.page.clean()
        EditTeachers(self.page, self.cursor_db, name, self.db)
        self.page.update()

    def transition_list(self, number):
        self.page.clean()
        AdminGroup(self.page, self.cursor_db, number, self.db)
        self.page.update()

    def transition_edit_group(self, number):
        self.page.clean()
        EditGroup(self.page, self.cursor_db, number, self.db)
        self.page.update()


class AdminGroup:
    def __init__(self, page, cursor_db, number, db):
        self.page = page
        self.cursor_db = cursor_db
        self.number = number
        self.db = db
        self.page.horizontal_alignment = CrossAxisAlignment.CENTER
        self.page.vertical_alignment = MainAxisAlignment.CENTER
        self.lv = ListView(expand=1, spacing=10, padding=20, width=1000)
        self.list_motorcade = []

# кнопка добавление
        self.floating_action_button_students = FloatingActionButton(icon=icons.ADD, on_click=self.fab_pressed_students,
                                                                    bgcolor=colors.LIME_300)
        self.page.add(self.floating_action_button_students)

# CupertinoSlidingSegmentedButton
        self.page.add(
            Row(
                [
                    IconButton(icons.ARROW_BACK, on_click=self.click_arrow),
                ],
                alignment=MainAxisAlignment.START,
            )
        )
        self.cursor_db.execute(f"SELECT name FROM group{self.number}")
        for i in self.cursor_db:
            self.list_motorcade.append(i)

# контейнер
        self.list_name = [x[0] for x in self.list_motorcade]
        self.len_list = len(self.list_name)

        for i in range(self.len_list):
            card_container = Container(
                content=Column(
                    [
                        ListTile(
                            title=Text(f"{self.list_name[i]}", size=40),
                            leading=Icon(icons.ACCOUNT_BOX, size=50),
                            trailing=PopupMenuButton(
                                icon=icons.MORE_VERT,
                                items=[
                                    PopupMenuItem(text="Аккаунт", on_click=lambda _, name=self.list_name[i]: print(name)),
                                    PopupMenuItem(text="Изменить",
                                                  on_click=lambda _, name=self.list_name[i]: self.transition_class_edit(name)),
                                    PopupMenuItem(text="Удалить"),
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

    def fab_pressed_students(self, e):
        self.page.clean()
        AddStudent(self.page, self.cursor_db, self.db, self.number, 0, 0)
        self.page.update()

    def click_arrow(self, e):
        self.page.clean()
        Admin(self.page, self.cursor_db, self.db)
        self.page.update()

    def transition_class_edit(self, name):
        self.page.clean()
        EditStudent(self.page, self.cursor_db, name, self.db, self.number, 0)
        self.page.update()


class AccountTeachers:
    def __init__(self, page, cursor_db, name, id, db):
        self.page = page
        self.id = id
        self.cursor_db = cursor_db
        self.name = name
        self.db = db
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
        self.cursor_db.execute(f"SELECT num_group FROM teachers WHERE name=='{name}'")

        self.list_motorcade = []
        self.cl_list_number = ''
        for i in self.cursor_db:
            self.list_motorcade.extend(map(str, i))  # делаем тип str

        for i in self.list_motorcade:
            self.cl_list_number = i

# Предметы в список
        self.cursor_db.execute(f"SELECT items FROM teachers WHERE name=='{name}'")

        self.list_motorcade = []
        self.cl_list_item = ''
        for i in self.cursor_db:
            self.list_motorcade.extend(map(str, i))  # делаем тип str

        for i in self.list_motorcade:
            self.cl_list_item = i

# ExpansionTile
        self.page.add(
            ExpansionTile(
                title=Text("Предметы", size=40, color="black"),
                controls=[ListTile(title=Text(f"{self.cl_list_item}", color='black', size=30))],
                width=700,
                bgcolor="#AFEEEE",
                collapsed_bgcolor="#AED6F1",

            ),
            ExpansionTile(
                title=Text("Группы", size=40, color="black"),
                controls=[ListTile(title=Text(f"{self.cl_list_number}", color='black', size=30))],
                width=700,
                bgcolor="#AFEEEE",
                collapsed_bgcolor="#AED6F1",
            ),
        )

    def click_arrow(self, e):
        self.page.clean()
        if self.id == 1:
            Admin(self.page, self.cursor_db, self.db)
        else:
            Numbers(self.page, self.cursor_db, self.id, self.db)
        self.page.update()


class SettingsAdmin:
    def __init__(self, page, cursor_db, id, db):
        self.page = page
        self.cursor_db = cursor_db
        self.id = id
        self.db = db

        self.cursor_db.execute(f"SELECT name, password, email FROM teachers WHERE rowid={id}")

        self.name_db = ''
        self.password = ''
        self.email = ''

        for i in self.cursor_db:
            self.name_db = str(i[0])
            self.password = str(i[1])
            self.email = str(i[2])

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
        Admin(self.page, self.cursor_db, self.db)
        self.page.update()

# кнопка сохранить
    def button_clicked(self, e):
        if self.text_name.value == '' or self.text_pass.value == '' or self.text_email.value == '':
            self.page.show_banner(self.bs)
        else:
            self.cursor_db.execute(f"UPDATE teachers SET name='{self.text_name.value}', password='{self.text_pass.value}', "
                                    f"email='{self.text_email.value}' WHERE rowid={self.id}")
            self.page.show_banner(self.dlg)
        self.page.update()
        self.db.commit()


class EditTeachers:
    def __init__(self, page, cursor_db, name, db):
        self.page = page
        self.cursor_db = cursor_db
        self.db = db
        self.name = name
        self.login = ''
        self.password = ''
        self.items = ''
        self.num_group = ''

        self.cursor_db.execute("SELECT num_group FROM group_db")

        self.list_num_group = []
        for i in self.cursor_db:
            self.list_num_group.extend(i)

        self.cursor_db.execute(f"SELECT login, password, items, num_group, rowid FROM teachers WHERE name='{name}'")
        for i in self.cursor_db:
            self.login = str(i[0])
            self.password = str(i[1])
            self.items = str(i[2])
            self.num_group = str(i[3])
            self.rowid = i[4]

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
        Admin(self.page, self.cursor_db, self.db)
        self.page.update()

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
                    self.cursor_db.execute(
                        f"UPDATE teachers SET name='{self.text_name.value}', password='{self.text_pass.value}', "
                        f"login='{self.text_login.value}', items='{self.text_items.value}', "
                        f"num_group='{self.text_num_group.value}' "
                        f"WHERE rowid={self.rowid}")
            except:
                self.error_write_num.value = ("ОШИБКА, в поле Группы нужно записывать через запятую и"
                                             " с одним пробелом после ")
                self.page.show_banner(self.bs)

        self.page.update()
        self.db.commit()


class AddGroup:
    def __init__(self, page, cursor_db, db):
        self.page = page
        self.cursor_db = cursor_db
        self.db = db

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
        Admin(self.page, self.cursor_db, self.db)
        self.page.update()

# кнопка сохранить
    def button_clicked(self, e):
        try:
            if self.text_num_group.value == '':
                self.page.show_banner(self.bs)
            elif 10000000 <= int(self.text_num_group.value) <= 99999999:
                self.page.show_banner(self.dlg)
                self.cursor_db.execute(f"INSERT INTO group_db VALUES('{self.text_num_group.value}')")
                self.cursor_db.execute(f"CREATE TABLE group{self.text_num_group.value}(name)")
                self.text_num_group.value = ''
            else:
                self.page.show_banner(self.error)
            self.page.update()
            self.db.commit()
        except:
            self.page.show_banner(self.error)


class AddTeachers:
    def __init__(self, page, cursor_db, db):
        self.page = page
        self.cursor_db = cursor_db
        self.db = db

        self.cursor_db.execute("SELECT num_group FROM group_db")

        self.list_num_group = []
        for i in cursor_db:
            self.list_num_group.extend(i)

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
        Admin(self.page, self.cursor_db, self.db)
        self.page.update()

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
                    self.cursor_db.execute(f"INSERT INTO teachers VALUES('{self.text_name.value}', '{self.text_login.value}',"
                                               f"'{self.text_password.value}', '{self.text_items.value}', "
                                               f"'{self.text_num_group.value}', 'None')")
                    self.text_name.value = ''
                    self.text_login.value = ''
                    self.text_password.value = ''
                    self.text_items.value = ''
                    self.text_num_group.value = ''
                    self.page.update()
                    self.db.commit()
            except:
                self.error_write_num.value = ("ОШИБКА, в поле Группы нужно записывать через запятую и"
                                             " с одним пробелом после ")
                self.page.show_banner(self.bs)


class AddStudent:
    def __init__(self, page, cursor_db, db, group, status, id):
        self.page = page
        self.cursor_db = cursor_db
        self.db = db
        self.group = group
        self.status = status
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
        if self.status == 0:
            Admin(self.page, self.cursor_db, self.db)
        else:
            Card(self.group, self.page, self.cursor_db, id, self.db)
        self.page.update()

# кнопка сохранить
    def button_clicked(self, e):
        try:
            if self.text_name.value == '':
                self.page.show_banner(self.bs)
            else:
                self.page.show_banner(self.dlg)
                self.cursor_db.execute(f"INSERT INTO group{self.group} VALUES('{self.text_name.value}')")
                self.text_name.value = ''
            self.page.update()
            self.db.commit()
        except:
            self.page.show_banner(self.error)


class EditGroup:
    def __init__(self, page, cursor_db, number, db):
        self.page = page
        self.cursor_db = cursor_db
        self.db = db
        self.number = number
        self.num_group = ''

        self.cursor_db.execute(f"SELECT num_group FROM group_db")
        for i in self.cursor_db:
            self.num_group = i

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
        Admin(self.page, self.cursor_db, self.db)
        self.page.update()

# кнопка сохранить
    def button_clicked(self, e):
        if self.text_num_group.value == '':
            self.page.show_banner(self.bs)
        elif self.text_num_group.value in self.num_group:
            self.error_write.value = 'Такая группа уже есть'
            self.page.show_banner(self.error)
        elif 10000000 <= int(self.text_num_group.value) <= 99999999:
            self.page.show_banner(self.dlg)
            self.cursor_db.execute(f"UPDATE group_db SET num_group='{self.text_num_group.value}' WHERE num_group={self.number}")
            self.cursor_db.execute(f"ALTER TABLE group{self.number} RENAME TO group{self.text_num_group.value}")
            self.cursor_db.execute(f"UPDATE teachers SET "
                                       f"num_group = REPLACE(num_group, {self.number}, {self.text_num_group.value}) "
                                       f"WHERE num_group LIKE '%{self.number}%'")
        else:
            self.page.show_banner(self.error)

        self.page.update()
        self.db.commit()


class EditStudent:
    def __init__(self, page, cursor_db, name, db, number, status):
        self.page = page
        self.cursor_db = cursor_db
        self.db = db
        self.name = name
        self.number = number
        self.status = status

# виджеты
        self.text_name = TextField(label="ФИО", value=f'{name}', width=500, text_size=30,
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
        if self.status == 0:
            AdminGroup(self.page, self.cursor_db, self.number, self.db)
        else:
            Card(self.number, self.page, self.cursor_db, self.id, self.db)
        self.page.update()

# кнопка сохранить
    def button_clicked(self, e):
        if self.text_name.value == '':
            self.page.show_banner(self.bs)
        else:
            self.page.show_banner(self.dlg)
            self.cursor_db.execute(f"UPDATE group{self.number} SET name='{self.text_name.value}' WHERE name='{self.name}'")
        self.page.update()
        self.db.commit()


def main(page: Page):
    db = sqlite3.connect("bntu_db.db")

    page.theme_mode = 'light'
    Main(page, db)


app(target=main)