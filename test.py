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

# переход по темам
        def change_topic(e):
            if self.page.theme_mode == "light":
                self.page.theme_mode = 'dark'
                user_login.border_color = 'white'
                user_password.border_color = 'white'
            else:
                self.page.theme_mode = 'light'
                user_login.border_color = 'black'
                user_password.border_color = 'black'
            self.page.update()

# проверка, было что-то написано в логине и пароле
        def validate(e):
            if all([user_login.value, user_password.value]):
                btn_entry.disabled = False
            else:
                btn_entry.disabled = True
            self.page.update()

# аватар
        def avatar(name, id):
            self.page.clean()
            AccountTeachers(self.page, self.cursor_db, name, id, self.db)
            self.page.update()

# выход
        def logout():
            self.page.clean()
            Main(self.page, self.db)
            self.page.update()

# настройки
        def settings(id):
            self.page.clean()
            SettingsAdmin(self.page, self.cursor_db, id, self.db)
            self.page.update()

# проверка на вход
        def check_users(e):
            self.cursor_db.execute("SELECT rowid, login, password, name FROM teachers")
            for i in self.cursor_db:
                if (f'{user_login.value}', f'{user_password.value}') == (i[1], i[2]):
                    self.page.clean()
                    if i[0] == 1:
                        self.page.appbar = AppBar(
                            leading_width=20,
                            title=Text(f"БНТУ | BNTU   {i[3]}"),
                            bgcolor=colors.SURFACE_VARIANT,
                            actions=[
                                IconButton(icons.SETTINGS, on_click=lambda event: settings(i[0])),
                                IconButton(icons.SUNNY, on_click=change_topic),
                                PopupMenuButton(
                                    items=[
                                        PopupMenuItem(text="Тех. поддержка"),
                                        PopupMenuItem(text="Выход", on_click=lambda event: logout())
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
                                IconButton(icons.ACCOUNT_CIRCLE_OUTLINED, on_click=lambda event: avatar(i[3], i[0])),
                                IconButton(icons.SUNNY, on_click=change_topic),
                                PopupMenuButton(
                                    items=[
                                        PopupMenuItem(text="Тех. поддержка"),
                                        PopupMenuItem(text="Выход", on_click=lambda event: logout())
                                    ]
                                ),
                            ],
                        )
                        self.page.update()
                        Numbers(self.page, self.cursor_db, i[0])

# виджеты
        user_login = TextField(value="", width=300, text_align=TextAlign.LEFT, label="Логин", height=100,
                               on_change=validate)
        user_password = TextField(value="", width=300, text_align=TextAlign.LEFT, label="Пароль", password=True,
                                  can_reveal_password=True, height=80, on_change=validate)
        btn_entry = ElevatedButton(text="Войти", disabled=True, width=300, height=50, bgcolor='#B0E0E6', color='black',
                                   on_click=check_users)
# верхний бар
        self.page.appbar = AppBar(
            leading_width=20,
            title=Text("БНТУ | BNTU"),
            bgcolor=colors.SURFACE_VARIANT,
            actions=[
                IconButton(icons.SUNNY, on_click=change_topic),
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
                        user_login,
                        user_password,
                        btn_entry
                    ])
                ], alignment=MainAxisAlignment.CENTER
            )
        )


class Numbers:
    def __init__(self, page, cursor_db, id):
        self.page = page
        self.cursor_db = cursor_db
        page.vertical_alignment = MainAxisAlignment.CENTER
        page.horizontal_alignment = CrossAxisAlignment.CENTER
        list_num = ''

# делаем список из номеров групп
        self.cursor_db.execute(f"SELECT num_group FROM teachers WHERE rowid={id}")
        for i in self.cursor_db:
            num_group_str = i[0]
            list_num = num_group_str.replace(',', ' ').split()

# контейнеры и нажатие на них
        for i in list_num:
            def next_class(e, value=i):
                page.clean()
                page.update()
                Card(value, self.page, self.cursor_db, id)

            page.add(
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
    def __init__(self, value, page, cursor_db, id):
        self.page = page
        self.page.vertical_alignment = MainAxisAlignment.CENTER
        list_motorcade = []
        self.lv = ListView(expand=1, spacing=10, padding=20)
        self.table_lv = ListView(expand=1, spacing=10, padding=15, visible=False, width=1200)
        week_list = ['Имя', 'Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота']

# кнопка добавление
        def fab_pressed(e):
            print(1)

        self.floating_action_button = FloatingActionButton(icon=icons.ADD, on_click=fab_pressed,
                                                           bgcolor=colors.LIME_300)
        self.page.add(self.floating_action_button)

# Видимость областей
        def on_segment_change(e):
            if e.control.selected_index == 0:  # Cards
                self.lv.visible = True
                self.table_lv.visible = False
                self.floating_action_button.visible = True
                self.table2.visible = False
            elif e.control.selected_index == 1:  # Table
                self.lv.visible = False
                self.table_lv.visible = True
                self.floating_action_button.visible = False
                self.table2.visible = True
            else:  # Send
                self.lv.visible = False
                self.table_lv.visible = False
                self.floating_action_button.visible = False
                self.table2.visible = False
            self.page.update()

# стрелка назад
        def click_arrow(e):
            self.page.clean()
            Numbers(self.page, cursor_db, id)
            self.page.update()

# CupertinoSlidingSegmentedButton
        self.page.add(
            Row(
                [
                    IconButton(icons.ARROW_BACK, on_click=click_arrow),
                    CupertinoSlidingSegmentedButton(
                        selected_index=0,
                        thumb_color=colors.BLUE_400,
                        padding=padding.symmetric(0, 15),
                        controls=[
                            Text("КАРТОЧКИ", size=25),
                            Text("ТАБЛИЦА", size=25),
                            Text("ОТПРАВИТЬ", size=25),
                        ],
                        on_change=on_segment_change,
                    ),
                ], alignment=MainAxisAlignment.CENTER,
            )
        )

# Добавляем всё в список, где есть кортежи, а затем убираем кортежи
        cursor_db.execute(f"SELECT name FROM group{value}")
        for i in cursor_db:
            list_motorcade.append(i)

        list_name = [x[0] for x in list_motorcade]
        len_list = len(list_name)

# Контейнеры
        for i in range(len_list):
            card_container = Container(
                content=Column(
                    [
                        ListTile(
                            title=Text(f"{list_name[i]}", size=40),
                            leading=Icon(icons.ACCOUNT_BOX, size=50),
                            trailing=PopupMenuButton(
                                icon=icons.MORE_VERT,
                                items=[
                                    PopupMenuItem(text="Аккаунт", on_click=lambda _, name=list_name[i]: print(name)),
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

        columns2 = [DataColumn(Text(f"Column {i + 1}", color="black")) for i in range(6)]

        self.table2 = DataTable(
            width=880,
            bgcolor="white",
            border=border.all(2, "#00FF7F"),
            border_radius=5,
            vertical_lines=BorderSide(2, "black"),
            columns=columns2,
            visible=False
        )
        self.page.add(Container(
            content=self.table2,
            padding=padding.only(left=290)
        ))

        self.page.add(self.table_lv)


# таблица
        columns = [DataColumn(Text(f"{week_list[i]}", color="black")) for i in range(7)]

        rows = [
            DataRow([
                DataCell(
                    Container(
                        content=Text(f"{list_name[i]}" if j == 0 else "     Н", size=25, color="black"),
                        width=200 if j == 0 else None,
                        on_click=lambda e, n=j, a=i: print(f"Столбец {n + 1}, {list_name[a]}") if n != 0 else None,
                    )
                )
                for j in range(7)
            ])
            for i in range(len(list_name))
        ]

        table = DataTable(
            width=800,
            bgcolor="white",
            border=border.all(2, "#00FF7F"),
            border_radius=5,
            vertical_lines=BorderSide(2, "black"),
            columns=columns,
            rows=rows,
        )

        self.table_lv.controls.append(table)

# кнопки и месяц
        but = IconButton(icons.ARROW_CIRCLE_LEFT, icon_size=35)
        but_2 = IconButton(icons.ARROW_CIRCLE_RIGHT, icon_size=35)
        today = datetime.date.today()  # Получаем текущую дату
        month_name = calendar.month_name[today.month]  # Получаем имя месяца
        t = Text(f'{month_name}', size=40)
        self.page.add(
            Row(
                [
                    but,
                    t,
                    but_2
                ],
                alignment=MainAxisAlignment.CENTER
            )
        )


class Admin:
    def __init__(self, page, cursor_db, db):
        self.page = page
        self.page.horizontal_alignment = CrossAxisAlignment.CENTER
        self.page.vertical_alignment = MainAxisAlignment.CENTER
        self.teachers_lv = ListView(expand=1, spacing=10, padding=20, width=1000)
        self.students_lv = ListView(expand=1, spacing=10, padding=20, visible=False, width=500)
        list_motorcade = []

# кнопка добавление
        def fab_pressed_students(e):
            self.page.clean()
            AddGroup(self.page, cursor_db, db)
            self.page.update()

        def fab_pressed_teachers(e):
            self.page.clean()
            AddTeachers(self.page, cursor_db, db)
            self.page.update()

        self.floating_action_button_teachers = FloatingActionButton(icon=icons.ADD, on_click=fab_pressed_teachers,
                                                                    bgcolor=colors.LIME_300)

        self.floating_action_button_students = FloatingActionButton(icon=icons.ADD, on_click=fab_pressed_students,
                                                                    bgcolor=colors.LIME_300, visible=False)
        self.page.add(self.floating_action_button_teachers, self.floating_action_button_students)

# Видимость областей
        def on_segment_change(e):
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
                        on_change=on_segment_change,
                    ),
                ], alignment=MainAxisAlignment.CENTER,
            )
        )

# преподаватели card

        def transition_account(name):
            self.page.clean()
            AccountTeachers(self.page, cursor_db, name, 1, db)
            self.page.update()

        def transition_edit(name):
            self.page.clean()
            EditTeachers(self.page, cursor_db, name, db)
            self.page.update()

        cursor_db.execute("SELECT name FROM teachers")

        for i in cursor_db:
            list_motorcade.append(i)

        list_teachers = [x[0] for x in list_motorcade]
        len_list_teachers = len(list_teachers)

        for i in range(len_list_teachers-1):
            card_container = Container(
                content=Column(
                    [
                        ListTile(
                            title=Text(f"{list_teachers[i+1]}", size=40),
                            leading=Icon(icons.ACCOUNT_BOX, size=50),
                            trailing=PopupMenuButton(
                                icon=icons.MORE_VERT,
                                items=[
                                    PopupMenuItem(text="Аккаунт",
                                                  on_click=lambda _, name=list_teachers[i+1]: transition_account(name)),
                                    PopupMenuItem(text="Изменить",
                                                  on_click=lambda _, name=list_teachers[i+1]: transition_edit(name)),
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
        def transition_list(number):
            self.page.clean()
            AdminGroup(self.page, cursor_db, number, db)
            self.page.update()

        def transition_edit_group(number):
            self.page.clean()
            EditGroup(self.page, cursor_db, number, db)
            self.page.update()

        cursor_db.execute("SELECT num_group FROM group_db")

        list_num_group = []

        for i in cursor_db:
            list_num_group.extend(i)

        len_list_num_group = len(list_num_group)
        for i in range(len_list_num_group):
            card_container_student = Container(
                content=Column(
                    [
                        ListTile(
                            title=Text(f"{list_num_group[i]}", size=70),
                            trailing=PopupMenuButton(
                                icon=icons.MORE_VERT,
                                items=[
                                    PopupMenuItem(text="Список",
                                                  on_click=lambda _, number=list_num_group[i]: transition_list(number)),
                                    PopupMenuItem(text="Изменить",
                                                  on_click=lambda _, number=list_num_group[i]:
                                                  transition_edit_group(number)),
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


class AdminGroup:
    def __init__(self, page, cursor_db, number, db):
        self.page = page
        self.page.horizontal_alignment = CrossAxisAlignment.CENTER
        self.page.vertical_alignment = MainAxisAlignment.CENTER
        self.lv = ListView(expand=1, spacing=10, padding=20, width=1000)
        list_motorcade = []

# кнопка добавление
        def fab_pressed_students(e):
            self.page.clean()
            AddStudent(self.page, cursor_db, db, number)
            self.page.update()

        self.floating_action_button_students = FloatingActionButton(icon=icons.ADD, on_click=fab_pressed_students,
                                                                    bgcolor=colors.LIME_300)
        self.page.add(self.floating_action_button_students)

# стрелка назад
        def click_arrow(e):
            self.page.clean()
            Admin(self.page, cursor_db, db)
            self.page.update()

# CupertinoSlidingSegmentedButton
        self.page.add(
            Row(
                [
                    IconButton(icons.ARROW_BACK, on_click=click_arrow),
                ],
                alignment=MainAxisAlignment.START,
            )
        )
        cursor_db.execute(f"SELECT name FROM group{number}")
        for i in cursor_db:
            list_motorcade.append(i)

        list_name = [x[0] for x in list_motorcade]
        len_list = len(list_name)

# Контейнеры
        def transition_class_edit(name):
            self.page.clean()
            EditStudent(self.page, cursor_db, name, db, number)
            self.page.update()

        for i in range(len_list):
            card_container = Container(
                content=Column(
                    [
                        ListTile(
                            title=Text(f"{list_name[i]}", size=40),
                            leading=Icon(icons.ACCOUNT_BOX, size=50),
                            trailing=PopupMenuButton(
                                icon=icons.MORE_VERT,
                                items=[
                                    PopupMenuItem(text="Аккаунт", on_click=lambda _, name=list_name[i]: print(name)),
                                    PopupMenuItem(text="Изменить",
                                                  on_click=lambda _, name=list_name[i]: transition_class_edit(name)),
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


class AccountTeachers:
    def __init__(self, page, cursor_db, name, id, db):
        self.page = page
        self.id = id
        self.page.horizontal_alignment = CrossAxisAlignment.CENTER
        self.page.vertical_alignment = MainAxisAlignment.START

# стрелка назад
        def click_arrow(e):
            self.page.clean()
            if self.id == 1:
                Admin(self.page, cursor_db, db)
            else:
                Numbers(self.page, cursor_db, id)
            self.page.update()

        self.page.add(
            Row(
                [
                    IconButton(icons.ARROW_BACK, on_click=click_arrow),
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
        cursor_db.execute(f"SELECT num_group FROM teachers WHERE name=='{name}'")

        list_motorcade = []
        cl_list_number = ''
        for i in cursor_db:
            list_motorcade.extend(map(str, i))  # делаем тип str

        for i in list_motorcade:
            cl_list_number = i

# Предметы в список
        cursor_db.execute(f"SELECT items FROM teachers WHERE name=='{name}'")

        list_motorcade = []
        cl_list_item = ''
        for i in cursor_db:
            list_motorcade.extend(map(str, i))  # делаем тип str

        for i in list_motorcade:
            cl_list_item = i


# ExpansionTile
        self.page.add(
            ExpansionTile(
                title=Text("Предметы", size=40, color="black"),
                controls=[ListTile(title=Text(f"{cl_list_item}", color='black', size=30))],
                width=700,
                bgcolor="#AFEEEE",
                collapsed_bgcolor="#AED6F1",

            ),
            ExpansionTile(
                title=Text("Группы", size=40, color="black"),
                controls=[ListTile(title=Text(f"{cl_list_number}", color='black', size=30))],
                width=700,
                bgcolor="#AFEEEE",
                collapsed_bgcolor="#AED6F1",
            ),
        )


class SettingsAdmin:
    def __init__(self, page, cursor_db, id, db):
        self.page = page
        self.cursor_db = cursor_db
        self.id = id
        self.db = db

# кнопка назад
        def click_end(e):
            self.page.clean()
            Admin(self.page, cursor_db, db)
            self.page.update()

# кнопка сохранить
        def button_clicked(e):
            if text_name.value == '' or text_pass.value == '' or text_email.value == '':
                self.page.show_banner(self.bs)
            else:
                self.cursor_db.execute(f"UPDATE teachers SET name='{text_name.value}', password='{text_pass.value}', "
                                       f"email='{text_email.value}' WHERE rowid={self.id}")
                self.page.show_banner(self.dlg)
            self.page.update()
            self.db.commit()

        self.cursor_db.execute(f"SELECT name, password, email FROM teachers WHERE rowid={id}")

        name_db = ''
        password = ''
        email = ''

        for i in cursor_db:
            name_db = str(i[0])
            password = str(i[1])
            email = str(i[2])

# виджеты
        t = Text("Имя и почта будут использоваться в тех.поддержке для связи с вами, для помощи", size=12)
        text_name = TextField(label="Имя", value=f'{name_db}', width=500, text_size=30,
                              border_color="#28B463", border_width=2)
        text_pass = TextField(label="Пароль", value=f'{password}', width=500, text_size=30,
                              password=True, can_reveal_password=True, border_color="#28B463", border_width=2)
        text_email = TextField(label="Почта", value=f'{email}', width=500, text_size=30,
                               border_color="#28B463", border_width=2)
        but_save = ElevatedButton(text="Сохранить", on_click=button_clicked, width=200, height=50)
        but_end = ElevatedButton(text="Назад", on_click=click_end, width=200, height=50)

# добавляем виджеты
        self.page.add(
            Column(
                [
                    text_email,
                    text_name,
                    text_pass,
                    t,
                ],
                alignment=MainAxisAlignment.CENTER,
                horizontal_alignment=CrossAxisAlignment.CENTER

            ),
            Row([
                but_end,
                but_save,
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


class EditTeachers:
    def __init__(self, page, cursor_db, name, db):
        self.page = page
        self.cursor_db = cursor_db
        self.db = db
        login = ''
        password = ''
        items = ''
        num_group = ''

        self.cursor_db.execute("SELECT num_group FROM group_db")

        list_num_group = []
        for i in cursor_db:
            list_num_group.extend(i)

        self.cursor_db.execute(f"SELECT login, password, items, num_group, rowid FROM teachers WHERE name='{name}'")
        for i in self.cursor_db:
            login = str(i[0])
            password = str(i[1])
            items = str(i[2])
            num_group = str(i[3])
            rowid = i[4]

# кнопка назад
        def click_end(e):
            self.page.clean()
            Admin(self.page, cursor_db, db)
            self.page.update()

# кнопка сохранить
        def button_clicked(e):
            if text_name.value == '' or text_pass.value == '' or text_login.value == '':
                self.page.show_banner(self.bs)
            elif text_items.value == '' or text_num_group.value == '':
                self.page.show_banner(self.bs)
            else:
                # проверка на правильные числа
                list_num = text_num_group.value.split(", ")
                kol_right = 0
                try:
                    for num in list_num:
                        if int(num) not in list_num_group:
                            error.value = f'Такого номера группы ({num}) нету в базе'
                            self.page.show_banner(self.error)
                        else:
                            kol_right += 1

                    if kol_right == len(list_num):
                        self.page.show_banner(self.dlg)
                        self.cursor_db.execute(
                            f"UPDATE teachers SET name='{text_name.value}', password='{text_pass.value}', "
                            f"login='{text_login.value}', items='{text_items.value}', "
                            f"num_group='{text_num_group.value}' "
                            f"WHERE rowid={rowid}")
                except:
                    error_write_num.value = ("ОШИБКА, в поле Группы нужно записывать через запятую и"
                                             " с одним пробелом после ")
                    self.page.show_banner(self.bs)

            self.page.update()
            self.db.commit()


# виджеты
        text_name = TextField(label="Имя", value=f'{name}', width=500, text_size=30,
                              border_color="#28B463", border_width=2)
        text_pass = TextField(label="Пароль", value=f'{password}', width=500, text_size=30,
                              password=True, can_reveal_password=True, border_color="#28B463", border_width=2)
        text_login = TextField(label="Логин", value=f'{login}', width=500, text_size=30,
                               border_color="#28B463", border_width=2)
        text_items = TextField(label="Предметы", value=f'{items}', width=500, text_size=30,
                               border_color="#28B463", border_width=2)
        text_num_group = TextField(label="Группы", value=f'{num_group}', width=500, text_size=30,
                                   border_color="#28B463", border_width=2)
        but_save = ElevatedButton(text="Сохранить", on_click=button_clicked, width=200, height=50)
        but_end = ElevatedButton(text="Назад", on_click=click_end, width=200, height=50)

# добавляем виджеты
        self.page.add(
            Column(
                [
                    text_name,
                    text_login,
                    text_pass,
                    text_items,
                    text_num_group
                ],
                alignment=MainAxisAlignment.CENTER,
                horizontal_alignment=CrossAxisAlignment.CENTER

            ),
            Row([
                but_end,
                but_save,
            ],
                alignment=MainAxisAlignment.CENTER,
                vertical_alignment=CrossAxisAlignment.CENTER
            )
        )

# уведомление
        error_write_num = Text("Нельзя,чтоб были пустые поля", size=20, color="red")
        self.bs = BottomSheet(
            content=Container(
                padding=50,
                content=Column(
                    tight=True,
                    controls=[
                        error_write_num
                    ],
                ),
            ),
        )

        self.dlg = AlertDialog(
            title=Text("УСПЕШНО!", size=50, color="green"),
        )

        error = Text('', size=20, color="red")
        self.error = AlertDialog(
            title=Text("ОШИБКА", size=50, color="red"),
            content=Column(
                tight=True,
                controls=[
                    error,
                    Text("Сперва добавьте группу", size=20, color="red"),
                ],
            ),
        )


class AddGroup:
    def __init__(self, page, cursor_db, db):
        self.page = page
        self.cursor_db = cursor_db
        self.db = db

# кнопка назад
        def click_end(e):
            self.page.clean()
            Admin(self.page, cursor_db, db)
            self.page.update()

# кнопка сохранить
        def button_clicked(e):
            try:
                if text_num_group.value == '':
                    self.page.show_banner(self.bs)
                elif 10000000 <= int(text_num_group.value) <= 99999999:
                    self.page.show_banner(self.dlg)
                    self.cursor_db.execute(f"INSERT INTO group_db VALUES('{text_num_group.value}')")
                    self.cursor_db.execute(f"CREATE TABLE group{text_num_group.value}(name)")
                    text_num_group.value = ''
                else:
                    self.page.show_banner(self.error)
                self.page.update()
                self.db.commit()
            except:
                self.page.show_banner(self.error)

# виджеты
        text_num_group = TextField(label="Номер группы", width=500, text_size=30,
                                   border_color="#28B463", border_width=2)
        but_save = ElevatedButton(text="Добавить", on_click=button_clicked, width=200, height=50)
        but_end = ElevatedButton(text="Назад", on_click=click_end, width=200, height=50)

# добавляем виджеты
        self.page.add(
            Column(
                [
                    text_num_group
                ],
                alignment=MainAxisAlignment.CENTER,
                horizontal_alignment=CrossAxisAlignment.CENTER

            ),
            Row([
                but_end,
                but_save,
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


class AddTeachers:
    def __init__(self, page, cursor_db, db):
        self.page = page
        self.cursor_db = cursor_db
        self.db = db

        self.cursor_db.execute("SELECT num_group FROM group_db")

        list_num_group = []
        for i in cursor_db:
            list_num_group.extend(i)

# кнопка назад
        def click_end(e):
            self.page.clean()
            Admin(self.page, cursor_db, db)
            self.page.update()

# кнопка сохранить
        def button_clicked(e):
            if text_name.value == '' or text_password.value == '' or text_login.value == '':
                self.page.show_banner(self.bs)
            elif text_items.value == '' or text_num_group.value == '':
                self.page.show_banner(self.bs)
            else:
                # проверка на правильные числа
                list_num = text_num_group.value.split(", ")
                kol_right = 0
                try:
                    for num in list_num:
                        if int(num) not in list_num_group:
                            error_num.value = f'Такого номера группы ({num}) нету в базе'
                            self.page.show_banner(self.error)
                        else:
                            kol_right += 1

                    if kol_right == len(list_num):
                        self.page.show_banner(self.dlg)
                        self.cursor_db.execute(f"INSERT INTO teachers VALUES('{text_name.value}', '{text_login.value}',"
                                               f"'{text_password.value}', '{text_items.value}', "
                                               f"'{text_num_group.value}', 'None')")
                        text_name.value = ''
                        text_login.value = ''
                        text_password.value = ''
                        text_items.value = ''
                        text_num_group.value = ''
                        self.page.update()
                        self.db.commit()
                except:
                    error_write_num.value = ("ОШИБКА, в поле Группы нужно записывать через запятую и"
                                             " с одним пробелом после ")
                    self.page.show_banner(self.bs)


# виджеты
        text_name = TextField(label="ФИО", width=500, text_size=30,
                              border_color="#28B463", border_width=2)
        text_login = TextField(label="Логин", width=500, text_size=30,
                               border_color="#28B463", border_width=2)
        text_password = TextField(label="Пароль", width=500, text_size=30,
                                  password=True, can_reveal_password=True, border_color="#28B463", border_width=2)
        text_items = TextField(label="Предметы", width=500, text_size=30,
                               border_color="#28B463", border_width=2)
        text_num_group = TextField(label="Номер группы", width=500, text_size=30,
                                   border_color="#28B463", border_width=2)
        but_save = ElevatedButton(text="Добавить", on_click=button_clicked, width=200, height=50)
        but_end = ElevatedButton(text="Назад", on_click=click_end, width=200, height=50)

        # добавляем виджеты
        self.page.add(
            Column(
                [
                    text_name,
                    text_login,
                    text_password,
                    text_items,
                    text_num_group
                ],
                alignment=MainAxisAlignment.CENTER,
                horizontal_alignment=CrossAxisAlignment.CENTER

            ),
            Row([
                but_end,
                but_save,
            ],
                alignment=MainAxisAlignment.CENTER,
                vertical_alignment=CrossAxisAlignment.CENTER
            )
        )

# уведомление
        error_write_num = Text("Нельзя,чтоб были пустые поля", size=20, color="red")
        self.bs = BottomSheet(
            content=Container(
                padding=50,
                content=Column(
                    tight=True,
                    controls=[
                        error_write_num
                    ],
                ),
            ),
        )

        self.dlg = AlertDialog(
            title=Text("УСПЕШНО!", size=50, color="green"),
        )

        error_num = Text('', size=20, color="red")
        self.error = AlertDialog(
            title=Text("ОШИБКА", size=50, color="red"),
            content=Column(
                tight=True,
                controls=[
                    error_num,
                    Text("Сперва добавьте группу", size=20, color="red"),
                ],
            ),
        )


class AddStudent:
    def __init__(self, page, cursor_db, db, group):
        self.page = page
        self.cursor_db = cursor_db
        self.db = db

# кнопка назад
        def click_end(e):
            self.page.clean()
            Admin(self.page, cursor_db, db)
            self.page.update()

# кнопка сохранить
        def button_clicked(e):
            try:
                if text_name.value == '':
                    self.page.show_banner(self.bs)
                else:
                    self.page.show_banner(self.dlg)
                    self.cursor_db.execute(f"INSERT INTO group{group} VALUES('{text_name.value}')")
                    text_name.value = ''
                self.page.update()
                self.db.commit()
            except:
                self.page.show_banner(self.error)

# виджеты
        text_name = TextField(label="ФИО", width=500, text_size=30,
                              border_color="#28B463", border_width=2)
        but_save = ElevatedButton(text="Добавить", on_click=button_clicked, width=200, height=50)
        but_end = ElevatedButton(text="Назад", on_click=click_end, width=200, height=50)

# добавляем виджеты
        self.page.add(
            Column(
                [
                    text_name
                ],
                alignment=MainAxisAlignment.CENTER,
                horizontal_alignment=CrossAxisAlignment.CENTER

            ),
            Row([
                but_end,
                but_save,
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


class EditGroup:
    def __init__(self, page, cursor_db, number, db):
        self.page = page
        self.cursor_db = cursor_db
        self.db = db
        num_group = ''

        self.cursor_db.execute(f"SELECT num_group FROM group_db")
        for i in self.cursor_db:
            num_group = i

# кнопка назад
        def click_end(e):
            self.page.clean()
            Admin(self.page, cursor_db, db)
            self.page.update()

# кнопка сохранить
        def button_clicked(e):
            if text_num_group.value == '':
                self.page.show_banner(self.bs)
            elif text_num_group.value in num_group:
                error_write.value = 'Такая группа уже есть'
                self.page.show_banner(self.error)
            elif 10000000 <= int(text_num_group.value) <= 99999999:
                self.page.show_banner(self.dlg)
                self.cursor_db.execute(f"UPDATE group_db SET num_group='{text_num_group.value}' WHERE num_group={number}")
                self.cursor_db.execute(f"ALTER TABLE group{number} RENAME TO group{text_num_group.value}")
                self.cursor_db.execute(f"UPDATE teachers SET "
                                       f"num_group = REPLACE(num_group, {number}, {text_num_group.value}) "
                                       f"WHERE num_group LIKE '%{number}%'")
            else:
                self.page.show_banner(self.error)

            self.page.update()
            self.db.commit()


# виджеты
        text_num_group = TextField(label="Группы", value=f'{number}', width=500, text_size=30,
                                   border_color="#28B463", border_width=2)
        but_save = ElevatedButton(text="Сохранить", on_click=button_clicked, width=200, height=50)
        but_end = ElevatedButton(text="Назад", on_click=click_end, width=200, height=50)

# добавляем виджеты
        self.page.add(
            Column(
                [
                    text_num_group,
                    Text('Номер группы автоматически обновится у преподавателей', size=15)
                ],
                alignment=MainAxisAlignment.CENTER,
                horizontal_alignment=CrossAxisAlignment.CENTER

            ),
            Row([
                but_end,
                but_save,
            ],
                alignment=MainAxisAlignment.CENTER,
                vertical_alignment=CrossAxisAlignment.CENTER
            )
        )

# уведомление
        error_write_num = Text("Нельзя,чтоб были пустые поля", size=20, color="red")
        self.bs = BottomSheet(
            content=Container(
                padding=50,
                content=Column(
                    tight=True,
                    controls=[
                        error_write_num
                    ],
                ),
            ),
        )

        self.dlg = AlertDialog(
            title=Text("УСПЕШНО!", size=50, color="green"),
        )

        error_write = Text('Должно быть 8 цифр', size=20, color="red")
        self.error = AlertDialog(
            title=Text("ОШИБКА", size=50, color="red"),
            content=Column(
                tight=True,
                controls=[
                    error_write,
                ],
            ),
        )


class EditStudent:
    def __init__(self, page, cursor_db, name, db, number):
        self.page = page
        self.cursor_db = cursor_db
        self.db = db

# кнопка назад
        def click_end(e):
            self.page.clean()
            Admin(self.page, cursor_db, db)
            self.page.update()

# кнопка сохранить
        def button_clicked(e):
            if text_name.value == '':
                self.page.show_banner(self.bs)
            else:
                self.page.show_banner(self.dlg)
                self.cursor_db.execute(f"UPDATE group{number} SET name='{text_name.value}' WHERE name='{name}'")
            self.page.update()
            self.db.commit()


# виджеты
        text_name = TextField(label="ФИО", value=f'{name}', width=500, text_size=30,
                              border_color="#28B463", border_width=2)
        but_save = ElevatedButton(text="Сохранить", on_click=button_clicked, width=200, height=50)
        but_end = ElevatedButton(text="Назад", on_click=click_end, width=200, height=50)

# добавляем виджеты
        self.page.add(
            Column(
                [
                    text_name
                ],
                alignment=MainAxisAlignment.CENTER,
                horizontal_alignment=CrossAxisAlignment.CENTER

            ),
            Row([
                but_end,
                but_save,
            ],
                alignment=MainAxisAlignment.CENTER,
                vertical_alignment=CrossAxisAlignment.CENTER
            )
        )

# уведомление
        error_write_num = Text("Нельзя,чтоб было пустое поле", size=20, color="red")
        self.bs = BottomSheet(
            content=Container(
                padding=50,
                content=Column(
                    tight=True,
                    controls=[
                        error_write_num
                    ],
                ),
            ),
        )

        self.dlg = AlertDialog(
            title=Text("УСПЕШНО!", size=50, color="green"),
        )


def main(page: Page):
    db = sqlite3.connect("bntu_db.db")

    page.theme_mode = 'light'
    Main(page, db)


app(target=main)
