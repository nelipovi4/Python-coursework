from flet import *
import datetime

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
                        PopupMenuItem(text="Выход"),
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
                                    PopupMenuItem(text="Руководство"),
                                    PopupMenuItem(text="Тех. поддержка"),
                                    PopupMenuItem(text="Выход из аккаунта", on_click=lambda event: self.logout())
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
                            PopupMenuButton(
                                icon=icons.ACCOUNT_CIRCLE_OUTLINED,
                                items=[
                                    PopupMenuItem(text="Аккаунт", on_click=lambda event: self.avatar(i[3], i[0])),
                                    PopupMenuItem(text="Выход из аккаунта", on_click=lambda event: self.logout())
                                ]
                            ),
                            IconButton(icons.SUNNY, on_click=self.change_topic),
                            PopupMenuButton(
                                items=[
                                    PopupMenuItem(text="Руководство"),
                                    PopupMenuItem(text="Настройки", on_click=lambda e: Settings(self.page, i[0], self.db)),
                                    PopupMenuItem(text="Тех. поддержка"),
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

        self.page.clean()
        self.page.update()

        self.settings_value = self.teacher.get_str(self.db.get_info_select_from("settings", f"teachers WHERE rowid='{self.id}'"))
        self.page.vertical_alignment = MainAxisAlignment.CENTER
        self.page.horizontal_alignment = CrossAxisAlignment.CENTER

        self.list_num = self.teacher.get_list_group(
            self.db.get_info_select_from_where("num_group", "teachers", "rowid", self.id)
        )

        if self.settings_value[0] == '0':
            self.click_cont_1()
        elif self.settings_value[0] == '1':
            self.click_cont_2()
        else:
            self.click_cont_3()

# контейнеры и нажатие на них
    def click_cont_1(self):

        # Генерация списка опций для Dropdown из list_num
        dropdown_options = [dropdown.Option(value) for value in self.list_num]

        # Переменная для хранения выбранного значения
        selected_value = {"value": None}

        drop_down = Dropdown(
            options=dropdown_options,
            text_size=20,
            on_change=lambda e: selected_value.update({"value": e.control.value}),
            width=360,
        )

        container = Container(
            content=Column(
                controls=[
                    drop_down,
                    Row([
                        ElevatedButton(
                            content=Text("ОТПРАВИТЬ", size=20),
                            width=175,
                            height=75,
                            on_click=lambda e: print(2)
                        ),
                        ElevatedButton(
                            content=Text("ТАБЛИЦА", size=20),
                            width=175,
                            height=75,
                            on_click=lambda e: Visible(self.page, self.id, self.db, selected_value['value'], 1)
                        ),
                    ])
                ]
            ),
            width=550,
            height=350,
            padding=100,
            bgcolor="#e3e3e3",
            border_radius=15
        )
        self.page.add(container)

    def click_cont_2(self):

        selected_number_ref = Ref[Text]()

        number = ["None"]
        for i in self.list_num:
            number.append(i)

        def handle_picker_change(e):
            selected_number_ref.current.value = number[int(e.data)]
            self.page.update()

        cupertino_picker = CupertinoPicker(
            selected_index=0,
            magnification=1.22,
            squeeze=1.2,
            item_extent=70,
            use_magnifier=True,
            on_change=handle_picker_change,
            controls=[Text(value=f, size=25) for f in number],
        )

        container = Container(
            content=Column(
                controls=[
                    Row(
                        controls=[
                            Text("Выберите группу:", size=25),
                            TextButton(
                                content=Text(value=number[0], ref=selected_number_ref, size=35),
                                style=ButtonStyle(color=colors.BLUE),
                                on_click=lambda e: self.page.show_banner(
                                    CupertinoBottomSheet(
                                        cupertino_picker,
                                        height=216,
                                        padding=padding.only(top=6),
                                    )
                                ),
                            ),
                        ],
                    ),
                    Row([
                        ElevatedButton(
                            content=Text("ОТПРАВИТЬ", size=20),
                            width=175,
                            height=75,
                            on_click=lambda e: print(2)
                        ),
                        ElevatedButton(
                            content=Text("ТАБЛИЦА", size=20),
                            width=175,
                            height=75,
                            on_click=lambda e: Visible(self.page, self.id, self.db, selected_number_ref.current.value, 1)
                        ),
                    ])
                ]
            ),
            width=550,
            height=300,
            padding=100,
            bgcolor="#e3e3e3",
            border_radius=15
        )
        self.page.add(container)

    def click_cont_3(self):
        scroll_cont = ListView(expand=1, width=500)
        for i in self.list_num:
            def next_class(e, value=i):
                Visible(self.page, self.id, self.db, value, self.statement.get_today_date())

            scroll_cont.controls.append(
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
        self.page.add(scroll_cont)


class Settings(Numbers):
    def __init__(self, pageN, id, db):
        super().__init__(pageN, id, db)
        self.radio_groups = None
        self.page.horizontal_alignment = CrossAxisAlignment.CENTER
        self.page.vertical_alignment = MainAxisAlignment.START

        self.page.clean()
        self.page.update()

        self.page.add(
            Row(
                [
                    IconButton(icons.ARROW_BACK, on_click=lambda e: Numbers(self.page, self.id, self.db)),
                ],
            ),
            Column([
                    Container(
                        Text("ГРУППЫ", size=70, style=TextStyle(letter_spacing=30)),
                        width=1500,
                        height=130,
                        alignment=alignment.center,
                        bgcolor="blue",
                        on_click=lambda e: self.show_content()
                    ),
                    Container(
                        Text("ТАБЛИЦА", size=70, style=TextStyle(letter_spacing=30)),
                        width=1500,
                        height=130,
                        alignment=alignment.center,
                        bgcolor="blue"
                    ),
            ], spacing=40)
        )

    def show_content(self):
        def handle_radio_change(e):
            selected_value = e.control.value
            for control in self.radio_groups:
                control.value = selected_value
            self.page.update()

        scroll_cont = ListView(width=800)
        self.radio_groups = [
            RadioGroup(
                value=self.settings_value[0],
                content=Row([
                    Radio(value="0", label="1"),
                ]),
                on_change=handle_radio_change
            ),
            RadioGroup(
                value=self.settings_value[0],
                content=Row([
                    Radio(value="1", label="2"),
                ]),
                on_change=handle_radio_change
            ),
            RadioGroup(
                value=self.settings_value[0],
                content=Row([
                    Radio(value="2", label="3"),
                ]),
                on_change=handle_radio_change
            )
        ]

        # Добавляем радио-группы в колонки
        scroll_cont.controls.append(Column(controls=[
            Row([Image(src="img/number_3.png"), self.radio_groups[0]]),
            Row([Image(src="img/number_2.png"), self.radio_groups[1]]),
            Row([Image(src="img/number_1.png"), self.radio_groups[2]]),
        ]))

        dialog = AlertDialog(
            title=Text("Выберите опцию"),
            content=scroll_cont,
            actions=[
                TextButton("Отмена", on_click=lambda e: self.page.close_banner()),
                TextButton("Сохранить", on_click=self.save_selection)
            ]
        )
        self.page.show_banner(dialog)

    def save_selection(self, e):
        selected_value = None
        for control in self.radio_groups:
            if control.value:
                selected_value = control.value
                continue
        if selected_value is not None:
            self.settings_value = f"{selected_value}" + self.settings_value[1:]
            self.db.set_info_update("teachers", f"settings={self.settings_value}", f"rowid='{self.id}'")
        self.page.close_banner()


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

        self.list_name = None
        self.date_lecture = None
        self.week_list_lecture = None
        self.date_consultation = None
        self.week_list_consultation = None
        self.date_practice_1 = None
        self.date_practice_2 = None
        self.list_subgroup_1 = None
        self.list_subgroup_2 = None
        self.list_subgroup_3 = None

        self.calculation_lecture()
        self.calculation_consultation()
        self.calculation_practice()

    def calculation_lecture(self):
        self.list_name = self.teacher.get_list_name(self.db.get_info_select_from("name", f"group{self.value}"))
        self.date_lecture = self.statement.get_list_date(self.teacher.get_list_name(
            self.db.get_info_select_from_where("dates", f"date_{self.value}", "type", "lecture"))
        )
        self.week_list_lecture = self.statement.get_list_week(self.date_lecture)

    def calculation_consultation(self):
        self.list_name = self.teacher.get_list_name(self.db.get_info_select_from("name", f"group{self.value}"))
        self.date_consultation = self.statement.get_list_date(self.teacher.get_list_name(
            self.db.get_info_select_from_where("dates", f"date_{self.value}", "type", "consultation"))
        )

        self.week_list_consultation = self.statement.get_list_week(self.date_consultation)

    def calculation_practice(self):
        self.list_name = self.teacher.get_list_name(self.db.get_info_select_from("name", f"group{self.value}"))
        self.date_practice_1 = self.statement.get_list_date(self.teacher.get_list_name(
            self.db.get_info_select_from("dates", f"date_{self.value} WHERE type='practice' AND subgroup='1'"))
        )
        self.date_practice_2 = self.statement.get_list_date(self.teacher.get_list_name(
            self.db.get_info_select_from("dates", f"date_{self.value} WHERE type='practice' AND subgroup='2'"))
        )
        self.list_subgroup_1 = self.teacher.get_list_name(
            self.db.get_info_select_from_where("name", f"group{self.value}", "subgroup", "1")
        )
        self.list_subgroup_2 = self.teacher.get_list_name(
            self.db.get_info_select_from_where("name", f"group{self.value}", "subgroup", "2")
        )
        self.list_subgroup_3 = self.teacher.get_list_name(
            self.db.get_info_select_from_where("name", f"group{self.value}", "subgroup", "None")
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


class Table(Card):
    def __init__(self, pageN, id, db, value, today_date):
        super().__init__(pageN, id, db, value, today_date)

        self.scroll_table_date_lecture = ListView(width=1200, height=60)
        self.scroll_table_lecture = ListView(expand=1, width=1200)
        self.scroll_table_date_consultation = ListView(width=1200, height=60, visible=False)
        self.scroll_table_consultation = ListView(expand=1, width=1200, visible=False)
        self.scroll_table_practice = ListView(expand=1, spacing=10, padding=15, width=1200, visible=False)

        self.selected_row_index = None
        self.columns_table_lecture = None
        self.row_table_lecture = None
        self.column_consultation = None
        self.rows_consultation = None
        self.rows_practice = None
        self.rows_practice_2 = None
        self.column_practice = None
        self.column_practice_2 = None
        self.radio_group_practice_grade = None
        self.dlg_practice = None
        self.radio_group = None
        self.text_date_lecture = None
        self.text_date_consultation = None
        self.dlg_lecture = None
        self.dlg_consultation = None
        self.text_date = None
        self.kol_lecture = 0
        self.kol_consultation = 0
        self.kol_practice_1 = 0
        self.kol_practice_2 = 0

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

        self.add_object_lecture_consultation()
        self.add_object_practice()

        self.create_table_lecture(self.date_lecture, self.week_list_lecture, self.list_name)
        self.create_table_consultation(self.date_consultation, self.week_list_consultation, self.list_name)
        self.create_table_practice(self.date_practice_1, self.date_practice_2, self.list_subgroup_1, self.list_subgroup_2)

    def create_table_lecture(self, list_date, list_week, list_name):
        # Таблица с датами ЛЕКЦИЯ
        columns_table_lecture_date = [DataColumn(Text(f"{list_date[i]}", color="black", size=18)) for i in range(6)]

        table_lecture_date = DataTable(
            width=875,
            bgcolor="white",
            border=border.all(2, "#00FF7F"),
            border_radius=5,
            vertical_lines=BorderSide(2, "black"),
            columns=columns_table_lecture_date,
        )
        container_table_lecture_date = Container(
            Row([
                IconButton(icons.ARROW_CIRCLE_LEFT_OUTLINED,
                           icon_size=35,
                           tooltip="Назад даты",
                           icon_color="#31A52E",
                           on_click=lambda e: self.move_arrow("left", self.date_lecture, "lecture", "None", "None")
                           ),
                IconButton(icons.DATE_RANGE_ROUNDED,
                           icon_size=35,
                           tooltip="Изменить порядок дат",
                           icon_color="#31A52E",
                           on_click=lambda e: self.edit_order_date(e, list_date, "lecture", "None", "None")
                           ),
                IconButton(icons.ADD_BOX,
                           icon_size=35,
                           tooltip="Добавить дату",
                           icon_color="#31A52E",
                           on_click=lambda e: self.add_date(e, "lecture", self.date_lecture, "None"),
                           ),
                PopupMenuButton(
                    icon=icons.EDIT_ROUNDED,
                    icon_color="#31A52E",
                    tooltip="Изменить",
                    icon_size=35,
                    items=[
                        PopupMenuItem(text="Удалить", icon=icons.CLOSE_SHARP,
                                      on_click=lambda e: self.delete_data(e, self.date_lecture, "lecture", "None")),
                        PopupMenuItem(text="Изменить", icon=icons.EDIT_SQUARE,
                                      on_click=lambda e: self.edit_data(e, self.date_lecture, "lecture", "None")),
                    ]
                ),
                IconButton(icons.ARROW_CIRCLE_RIGHT_OUTLINED,
                           icon_size=35,
                           tooltip="Вперёд даты",
                           icon_color="#31A52E",
                           on_click=lambda e: self.move_arrow("right", self.date_lecture, "lecture", "None", "None")
                           ),
                table_lecture_date,
            ], alignment=MainAxisAlignment.CENTER),
        )
        self.scroll_table_date_lecture.controls.append(container_table_lecture_date)
        # таблица основная ЛЕКЦИЯ
        self.columns_table_lecture = [
            DataColumn(Text("Имя" if i == 0 else f"{list_week[i - 1]}", color="black", size=15)) for i in range(7)]
        self.row_table_lecture = [  # i - строки | j - столбцы
            DataRow([
                DataCell(
                    Container(
                        content=Text(f"{list_name[i]}" if j == 0 else f"    {self.statement.check_which_value(
                            self.db.get_info_join(f"{list_name[i]}", f"{list_date[j - 1]}",
                                                  f"{self.value}", "lecture"))}",
                                     size=25, color="black"),
                        width=205 if j == 0 else None,
                    ),
                    on_tap=lambda e, n=j, a=i:
                    self.put_grade_student(list_date[n - 1], list_name[a], "lecture") if n != 0 else None,
                    on_double_tap=lambda e, n=j, row_index=i: self.handle_row_double_tap(row_index, "lecture", "None") if n == 0 else None
                )
                for j in range(7)
            ], )
            for i in range(len(list_name))
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

    def create_table_consultation(self, list_date, list_week, list_name):
        # Таблица с датами КОНСУЛЬТАЦИЯ
        column_table_consultation_date = [DataColumn(Text(f"{list_date[i]}", color="black", size=18))
                                          for i in range(6)]

        table_consultation_date = DataTable(
            width=875,
            bgcolor="white",
            border=border.all(2, "#061CF9"),
            border_radius=5,
            vertical_lines=BorderSide(2, "black"),
            columns=column_table_consultation_date,
        )
        container_table_consultation_date = Container(
            Row([
                IconButton(icons.ARROW_CIRCLE_LEFT_OUTLINED,
                           icon_size=35,
                           tooltip="Назад даты",
                           icon_color="#3056FF",
                           on_click=lambda e: self.move_arrow("left", self.date_consultation, "consultation", "None", "None")
                           ),
                IconButton(icons.DATE_RANGE_ROUNDED,
                           icon_size=35,
                           tooltip="Изменить порядок дат",
                           icon_color="#3056FF",
                           on_click=lambda e: self.edit_order_date(e, list_date, "consultation", "None", "None")
                           ),
                IconButton(icons.ADD_BOX,
                           icon_size=35,
                           tooltip="Добавить дату",
                           icon_color="#3056FF",
                           on_click=lambda e: self.add_date(e, "consultation", self.date_consultation, "None"),
                           ),
                PopupMenuButton(
                    icon=icons.EDIT_ROUNDED,
                    icon_color="#3056FF",
                    icon_size=35,
                    tooltip="Изменить",
                    items=[
                        PopupMenuItem(text="Удалить", icon=icons.CLOSE_SHARP,
                                      on_click=lambda e: self.delete_data(e, self.date_consultation,
                                                                                       "consultation", "None")),
                        PopupMenuItem(text="Изменить", icon=icons.EDIT_SQUARE,
                                      on_click=lambda e: self.edit_data(e, self.date_consultation,
                                                                                     "consultation", "None")),
                    ]
                ),
                IconButton(icons.ARROW_CIRCLE_RIGHT_OUTLINED,
                           icon_size=35,
                           tooltip="Вперёд даты",
                           icon_color="#3056FF",
                           on_click=lambda e: self.move_arrow("right", self.date_consultation, "consultation", "None", "None")
                           ),
                table_consultation_date
            ], alignment=MainAxisAlignment.CENTER),
        )

        self.scroll_table_date_consultation.controls.append(container_table_consultation_date)

        # таблица основная КОНСУЛЬТАЦИЯ
        self.column_consultation = [
            DataColumn(Text("Имя" if i == 0 else f"{list_week[i - 1]}", color="black", size=15)) for i
            in range(7)]
        self.rows_consultation = [  # i - строки | j - столбцы
            DataRow([
                DataCell(
                    Container(
                        content=Text(f"{list_name[i]}" if j == 0 else f"    {self.statement.check_which_value(
                            self.db.get_info_join(f"{list_name[i]}", f"{list_date[j - 1]}",
                                                  f"{self.value}", "consultation"))}",
                                     size=25, color="black"),
                        width=205 if j == 0 else None,
                    ), on_tap=lambda e, n=j, a=i:
                    self.put_grade_student(list_date[n - 1], list_name[a], "consultation")
                    if n != 0 else None,
                    on_double_tap=lambda e, n=j, row_index=i: self.handle_row_double_tap(row_index, "consultation", "None")
                    if n == 0 else None
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

    def create_table_practice(self, list_date_1, list_date_2, list_subgroup_1, list_subgroup_2):
        # ПРАКТИКА
        container_1 = Container(
            Row([
                Text("Подгруппа 1", size=30),
                IconButton(icons.ARROW_CIRCLE_LEFT_OUTLINED,
                           icon_size=35,
                           tooltip="Назад даты",
                           on_click=lambda e: self.move_arrow("left", list_date_1, "practice", list_date_2, "1")
                           )
                ,
                IconButton(icons.DATE_RANGE_ROUNDED,
                           icon_size=35,
                           tooltip="Изменить порядок дат",
                           on_click=lambda e: self.edit_order_date(e, list_date_1, "practice",  list_date_2, "1")
                           ),
                IconButton(icons.ADD_BOX,
                           icon_size=35,
                           tooltip="Добавить дату",
                           on_click=lambda e: self.add_date(e, "practice", list_date_1, "1")
                           ),
                PopupMenuButton(
                    icon=icons.EDIT_ROUNDED,
                    icon_size=35,
                    tooltip="Изменить",
                    items=[
                        PopupMenuItem(text="Удалить", icon=icons.CLOSE_SHARP,
                                      on_click=lambda e: self.delete_data(e, list_date_1, "practice", "1")),
                        PopupMenuItem(text="Изменить", icon=icons.EDIT_SQUARE,
                                      on_click=lambda e: self.edit_data(e, list_date_1, "practice", "1")),
                    ]
                ),
                IconButton(icons.ARROW_CIRCLE_RIGHT_OUTLINED,
                           icon_size=35,
                           tooltip="Вперёд даты",
                           on_click=lambda e: self.move_arrow("right", list_date_1, "practice", list_date_2, "1")
                           )
            ])
        )

        container_2 = Container(
            Row([
                Text("Подгруппа 2", size=30),
                IconButton(icons.ARROW_CIRCLE_LEFT_OUTLINED,
                           icon_size=35,
                           tooltip="Назад даты",
                           icon_color="#B26CF9",
                           on_click=lambda e: self.move_arrow("left", list_date_1, "practice", list_date_2, "2")
                           )
                ,
                IconButton(icons.DATE_RANGE_ROUNDED,
                           icon_size=35,
                           icon_color="#B26CF9",
                           tooltip="Изменить порядок дат",
                           on_click=lambda e: self.edit_order_date(e, list_date_2, "practice", list_date_1, "2")
                           ),
                IconButton(icons.ADD_BOX,
                           icon_size=35,
                           icon_color="#B26CF9",
                           tooltip="Добавить дату",
                           on_click=lambda e: self.add_date(e, "practice", list_date_2, "2")
                           ),
                PopupMenuButton(
                    icon=icons.EDIT_ROUNDED,
                    icon_color="#B26CF9",
                    tooltip="Изменить",
                    icon_size=35,
                    items=[
                        PopupMenuItem(text="Удалить", icon=icons.CLOSE_SHARP,
                                      on_click=lambda e: self.delete_data(e, list_date_2, "practice", "2")),
                        PopupMenuItem(text="Изменить", icon=icons.EDIT_SQUARE,
                                      on_click=lambda e: self.edit_data(e, list_date_2, "practice", "2")),
                    ]
                ),
                IconButton(icons.ARROW_CIRCLE_RIGHT_OUTLINED,
                           icon_size=35,
                           tooltip="Вперёд даты",
                           icon_color="#B26CF9",
                           on_click=lambda e: self.move_arrow("right", list_date_1, "practice", list_date_2, "2")
                           ),
            ])
        )

        # таблица 1
        self.column_practice = [
            DataColumn(Text("Имя" if i == 0 else f"{list_date_1[i - 1]}", color="black", size=20)) for i in
            range(7)]

        self.rows_practice = [  # i - строки | j - столбцы
            DataRow([
                DataCell(
                    Container(
                        content=Text(
                            f"{list_subgroup_1[i]}" if j == 0 else f"{self.statement.check_which_value_practice(
                                self.db.get_info_select_from("subgroup, value", f"statement_practice{self.value} WHERE "
                                                                                f"name='{list_subgroup_1[i]}'"
                                                                                f" AND date='{list_date_1[j - 1]}'"
                                                             ))}",
                            size=25, color="black"),
                        width=205 if j == 0 else None,
                    ), on_tap=lambda e, n=j, a=i:
                    self.put_grade_student(list_date_1[n - 1], list_subgroup_1[a], "practice")
                    if n != 0 else None,
                    on_double_tap=lambda e, n=j, row_index=i: self.handle_row_double_tap(row_index, "practice", "1")
                    if n == 0 else None
                )
                for j in range(7)
            ])
            for i in range(len(list_subgroup_1))
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
        self.column_practice_2 = [
            DataColumn(Text("Имя" if i == 0 else f"{list_date_2[i - 1]}", color="black", size=20)) for i in
            range(7)]
        self.rows_practice_2 = [  # i - строки | j - столбцы
            DataRow([
                DataCell(
                    Container(
                        content=Text(
                            f"{list_subgroup_2[i]}" if j == 0 else f"{self.statement.check_which_value_practice(
                                self.db.get_info_select_from("subgroup, value", f"statement_practice{self.value} WHERE "
                                                                                f"name='{list_subgroup_2[i]}'"
                                                                                f" AND date='{list_date_2[j - 1]}'"
                                                             ))}",
                            size=25, color="black"),
                        width=205 if j == 0 else None,
                    ), on_tap=lambda e, n=j, a=i:
                    self.put_grade_student(list_date_2[n - 1], list_subgroup_2[a], "practice")
                    if n != 0 else None,
                    on_double_tap=lambda e, n=j, row_index=i: self.handle_row_double_tap(row_index, "practice", "2")
                    if n == 0 else None
                )
                for j in range(7)
            ])
            for i in range(len(list_subgroup_2))
        ]

        table_practice_2 = DataTable(
            width=800,
            bgcolor="white",
            border=border.all(2, "#F90606"),
            border_radius=5,
            vertical_lines=BorderSide(2, "black"),
            columns=self.column_practice_2,
            rows=self.rows_practice_2,
        )
        self.scroll_table_practice.controls.append(container_1)
        self.scroll_table_practice.controls.append(table_practice_1)
        self.scroll_table_practice.controls.append(ElevatedButton(text="Изменить список подгрупп",
                                       icon=icons.ARTICLE_SHARP,
                                       width=300,
                                       on_click=lambda e: Subgroup(self.page, self.id, self.db, self.value, self.date),
                                       ))
        self.scroll_table_practice.controls.append(container_2)
        self.scroll_table_practice.controls.append(table_practice_2)

    def handle_row_double_tap(self, row_index, types, subgroup):
        row = None
        if types == "lecture":
            row = self.row_table_lecture
        elif types == "consultation":
            row = self.rows_consultation
        else:
            if subgroup == "1":
                row = self.rows_practice
            elif subgroup == "2":
                row = self.rows_practice_2

        # Если строка уже выделена и повторно кликнули на нее — сбрасываем выделение
        if self.selected_row_index == row_index:
            # Сбрасываем цвет для всей строки
            row[row_index].color = None

            # Сбрасываем индекс выделенной строки
            self.selected_row_index = None
        else:
            # Сбрасываем цвет для всех строк, чтобы убрать выделение с других строк
            for r in row:
                r.color = None

            # Устанавливаем цвет для новой выделенной строки — красный
            row[row_index].color = colors.with_opacity(0.4, "#9c9c9c")

            # Обновляем индекс выделенной строки
            self.selected_row_index = row_index

        # Обновляем интерфейс
        self.page.update()

    def edit_data(self, e, type_list, types, subgroup):

        def update_date(e, date, types, subgroup):
            self.page.show_banner(self.save)
            self.db.set_info_update(f"date_{self.value}", f"dates='{e.control.value.strftime('%d.%m.%Y')}'",
                                    f"dates='{date}' AND type='{types}' AND subgroup='{subgroup}'")
            self.db.set_info_update(f"statement_{types}{self.value}", f"date='{e.control.value.strftime('%d.%m.%Y')}'",
                                    f"date='{date}'")
            self.update_table(f"{types}")

        def date_calendar(e, date):
            self.page.close_banner()
            self.page.show_banner(
                DatePicker(
                    first_date=datetime.datetime(year=2024, month=9, day=1),
                    current_date=datetime.datetime(year=self.now.year, month=int(f"{date[3]}{date[4]}"),
                                                   day=int(f"{date[0]}{date[1]}")),
                    last_date=datetime.datetime(year=self.now.year, month=self.now.month, day=self.now.day),
                    on_change=lambda e: update_date(e, date, types, subgroup),
                    on_dismiss=lambda e: self.page.show_banner(self.cancel)
                )
            ),
            self.page.update()

        scroll_con = ListView(expand=1, spacing=10, padding=15, width=500)
        len_list = len(type_list)
        for i in range(len_list):
            if type_list[i] != "                 ":
                scroll_con.controls.append(
                    TextButton(
                        content=Text(f"{type_list[i]}", size=30),
                        on_click=lambda e, a=i: date_calendar(e, type_list[a])
                    )
                )
        self.page.show_banner(
            AlertDialog(
                title=Text("Изменить даты", size=40),
                content=Column(
                    [
                        scroll_con,
                    ]
                ),
                actions=[
                    TextButton(
                        content=Text("Отмена", size=20),
                        on_click=lambda e: self.page.close_banner()
                    ),

                ],
            )
        )

    def delete_data(self, e, type_list, types, subgroup):
        def delete(e, types, subgroup, data):
            self.db.delete_teachers(f"date_{self.value}",
                                    f"dates='{data}' AND type='{types}' AND subgroup='{subgroup}'")
            if subgroup == '1':
                for i in self.list_subgroup_1:
                    self.db.delete_teachers(f"statement_{types}{self.value}",
                                            f"date='{data}' AND name='{i}'")
            elif subgroup == '2':
                for i in self.list_subgroup_2:
                    self.db.delete_teachers(f"statement_{types}{self.value}",
                                            f"date='{data}' AND name='{i}'")
            else:
                self.db.delete_teachers(f"statement_{types}{self.value}",
                                        f"date='{data}'")
            self.page.show_banner(self.save)
            self.update_table(f"{types}")

        con = Container(content=Column(controls=[]), alignment=alignment.center)
        len_list = len(type_list)
        for i in range(len_list):
            if type_list[i] != "                 ":
                con.content.controls.append(
                    TextButton(
                        content=Text(f"{type_list[i]}", size=30),
                        on_click=lambda e, a=i: delete(e, types, subgroup, type_list[a])
                    )
                )

        self.page.show_banner(
            AlertDialog(
                title=Text("Удалить даты", size=40),
                content=Column(
                    [
                        con,
                    ]
                ),
                actions=[
                    TextButton(
                        content=Text("Отмена", size=20),
                    ),

                ],
            )
        )

    def update_table(self, types):

        if types == "lecture":
            self.scroll_table_lecture.controls.clear()
            self.scroll_table_date_lecture.controls.clear()

            self.calculation_lecture()

            self.create_table_lecture(self.date_lecture, self.week_list_lecture, self.list_name)
        elif types == "consultation":
            self.scroll_table_consultation.controls.clear()
            self.scroll_table_date_consultation.controls.clear()

            self.calculation_consultation()

            self.create_table_consultation(self.date_consultation, self.week_list_consultation, self.list_name)
        else:
            self.scroll_table_practice.controls.clear()

            self.calculation_practice()

            self.create_table_practice(self.date_practice_1, self.date_practice_2, self.list_subgroup_1, self.list_subgroup_2)
        self.page.update()

    def update_table_parameter(self, list_type, types, list_type_2):
        new_week_list = self.statement.get_list_week(list_type)
        if types == "lecture":
            self.scroll_table_lecture.controls.clear()
            self.scroll_table_date_lecture.controls.clear()

            self.calculation_lecture()

            self.create_table_lecture(list_type, new_week_list, self.list_name)
        elif types == "consultation":
            self.scroll_table_consultation.controls.clear()
            self.scroll_table_date_consultation.controls.clear()

            self.calculation_consultation()

            self.create_table_consultation(list_type, new_week_list, self.list_name)
        else:
            self.scroll_table_practice.controls.clear()

            self.calculation_practice()

            self.create_table_practice(list_type, list_type_2, self.list_subgroup_1, self.list_subgroup_2)
        self.page.update()

    def edit_order_date(self, e, list_type, types, list_type_2, subgroup):
        drag_targets = []
        scroll_con = ListView(expand=1, spacing=10, padding=15, width=1100)
        if types == "lecture":
            const_date_list = self.date_lecture
        elif types == "consultation":
            const_date_list = self.date_consultation
        else:
            if subgroup == "1":
                const_date_list = self.date_practice_1
            else:
                const_date_list = self.date_practice_2

        def drag_accept(e):
            src = self.page.get_control(e.src_id)
            e.control.content = Container(
                content=Text(src.content.content.value, color="black", size=30),
                width=170,
                height=60,
                bgcolor="green",
                border_radius=5,
                alignment=alignment.center
            )
            e.control.border = None
            e.control.update()

        # Разбиваем элементы на строки по 6 элементов
        rows = [
            Row(
                [
                    Draggable(
                        group="color",
                        content=Container(
                            content=Text(item, color="black", size=30),
                            width=170,
                            height=60,
                            bgcolor="#b2c3f5",
                            border_radius=5,
                            alignment=alignment.center
                        ),
                    ) for item in const_date_list[i:i + 6] if item != "                 "
                ]
            ) for i in range(0, len(list_type), 6)
        ]

        # Создаем основной контейнер, содержащий строки
        draggable_container = Container(
            content=Column(
                [
                    Draggable(
                        group="color",
                        content=Container(
                            content=Text("                 "),
                            width=170,
                            height=60,
                            bgcolor="#fdbcb8",
                            border_radius=5,
                        ),
                    ),
                    Column(rows)
                ]
            )
        )

        scroll_con.controls.append(draggable_container)

        # Создаем список DragTarget для приёма Draggable элементов
        for i in range(6):
            drag_targets.append(
                DragTarget(
                    group="color",
                    content=Container(
                        content=Text(f"{list_type[i]}", size=30, color="black"),
                        width=170,
                        height=60,
                        bgcolor=colors.BLUE_GREY_100,
                        border_radius=5,
                        alignment=alignment.center,
                    ),
                    on_accept=drag_accept,
                )
            )

        def print_drag_target_text(e):
            for i, drag_target in enumerate(drag_targets):
                list_type[i] = f"{drag_target.content.content.value}"
            if subgroup == "2":
                self.update_table_parameter(list_type_2, types, list_type)
            else:
                self.update_table_parameter(list_type, types, list_type_2)
            self.page.close_banner()
            self.page.update()

        # Отображаем диалоговое окно с Draggable и DragTarget элементами
        self.page.show_banner(
            AlertDialog(
                title=Text("Изменить даты", size=40),
                content=Column(
                    [
                        scroll_con,  # Добавляем scroll_con с Draggable контейнером
                        Row(drag_targets),  # Добавляем строку с DragTarget
                    ]
                ),
                actions=[
                    TextButton(
                        content=Text("Сохранить", size=20),
                        on_click=print_drag_target_text
                    ),
                    TextButton(
                        content=Text("Отмена", size=20),
                        on_click=lambda e: self.page.close_banner()
                    ),

                ],
            )
        )

    def put_grade_student(self, date, name, types):
        if date == "                 ":
            self.page.show_banner(self.banner)
        else:
            value_t = self.statement.check_which_value(self.db.get_info_join(f"{name}", f"{date}",
                                                                             f"{self.value}", f"{types}"))
            self.radio_group.value = value_t  # значение для radio button
            if types == "practice":
                value_g = self.statement.check_which_value(self.db.get_info_select_from("subgroup",
                                                                                        f"statement_practice{self.value} "
                                                                                        f"WHERE name='{name}' "
                                                                                        f"AND date='{date}'"))
                self.radio_group_practice_grade.value = value_g
                self.text_date.value = f"{name} | {date}"
                self.page.show_banner(self.dlg_practice)
            elif types == "lecture":
                self.text_date.value = f"{name} | {date}"
                self.page.show_banner(self.dlg_lecture)
            elif types == "consultation":
                self.text_date.value = f"{name} | {date}"
                self.page.show_banner(self.dlg_consultation)

    def show_window_save(self, e, types):
        name, date = self.text_date.value.split(" | ")  # отделяем имя, дату
        self.db.delete_info_statement(f"{name}", f"{date}", f"{self.value}", f"{types}")
        if types != "practice":
            if self.radio_group.value != " .":
                self.db.insert_info_values(f"statement_{types}{self.value}", f"'{name}', '{date}', "
                                                                             f"'{self.radio_group.value}'")
        else:
            if self.radio_group.value != " ." or self.radio_group_practice_grade.value != " .":
                self.db.insert_info_values(f"statement_{types}{self.value}", f"'{name}', '{date}', "
                                                                              f"'{self.radio_group.value}', "
                                                                              f"'{self.radio_group_practice_grade.value}'")

        self.page.show_banner(self.save)
        self.update_table(f"{types}")

    def add_date(self, e, types, date, subgroup):
        def add_date_in_db(e):
            if e.control.value.strftime('%d.%m.%Y') in date:
                self.page.show_banner(self.error_date)
            else:
                self.db.insert_info_values(f"date_{self.value}",
                                           f"'{e.control.value.strftime('%d.%m.%Y')}', '{types}', '{subgroup}'")
            self.update_table(f"{types}")

        self.page.show_banner(
            DatePicker(
                first_date=datetime.datetime(year=2024, month=9, day=1),
                last_date=datetime.datetime(year=self.now.year, month=self.now.month, day=self.now.day),
                on_change=lambda e: add_date_in_db(e),
            )
        ),

    def move_arrow(self, left_or_right, list_type, types, list_type_2, subgroup):
        def check_data_left(const_list, lists):
            if const_list > 0:
                const_list -= 1
                for i in range(6):
                    new_date_list.append(lists[i - 6 * const_list])
                return new_date_list, const_list
            else:
                return lists, const_list

        def check_data_right(const_list, lists):
            if const_list < (len(lists) / 6) - 1:
                const_list += 1
                for i in range(6):
                    new_date_list.append(lists[i + 6 * const_list])
                return new_date_list, const_list
            else:
                return lists, None

        new_date_list = []
        if left_or_right == "left":
            if types == "lecture":
                new_date_list, new_const_list = check_data_left(self.kol_lecture, list_type)
                self.kol_lecture = new_const_list
                self.update_table_parameter(new_date_list, types, "None")
            elif types == "consultation":
                new_date_list, new_const_list = check_data_left(self.kol_consultation, list_type)
                self.kol_consultation = new_const_list
                self.update_table_parameter(new_date_list, types, "None")
            else:
                if subgroup == "1":
                    new_date_list, new_const_list = check_data_left(self.kol_practice_1, self.date_practice_1)
                    self.kol_practice_1 = new_const_list
                    self.update_table_parameter(new_date_list, types, list_type_2)
                else:
                    new_date_list, new_const_list = check_data_left(self.kol_practice_2, self.date_practice_2)
                    self.kol_practice_2 = new_const_list
                    self.update_table_parameter(list_type, types, new_date_list)
        else:
            if types == "lecture":
                new_date_list, new_const_list = check_data_right(self.kol_lecture, list_type)
                if new_const_list is not None:
                    self.kol_lecture = new_const_list
                    self.update_table_parameter(new_date_list, types, "None")
            elif types == "consultation":
                new_date_list, new_const_list = check_data_right(self.kol_consultation, list_type)
                if new_const_list is not None:
                    self.kol_consultation = new_const_list
                    self.update_table_parameter(new_date_list, types, "None")
            else:
                if subgroup == "1":
                    new_date_list, new_const_list = check_data_right(self.kol_practice_1, self.date_practice_1)
                    if new_const_list is not None:
                        self.kol_practice_1 = new_const_list
                        self.update_table_parameter(new_date_list, types, list_type_2)
                else:
                    new_date_list, new_const_list = check_data_right(self.kol_practice_2, self.date_practice_2)
                    if new_const_list is not None:
                        self.kol_practice_2 = new_const_list
                        self.update_table_parameter(list_type, types, new_date_list)

    def add_object_lecture_consultation(self):
        # radio button
        self.radio_group = RadioGroup(content=Row([
            Radio(value=" 1", label="1", tooltip="1 час пропуска"),
            Radio(value=" 2", label="2", tooltip="2 часа пропуска"),
            Radio(value="1y", label="1y", tooltip="1 час (уважительно)"),
            Radio(value="2y", label="2y", tooltip="2 часа (уважительно)"),
            Radio(value=" .", label="Пусто", tooltip="Очистить поле")
        ]))

        self.text_date = Text("")
        self.dlg_lecture = AlertDialog(
            title=self.text_date,
            content=Row(
                controls=[
                    self.radio_group
                ]
            ),
            actions=[
                TextButton("Сохранить", on_click=lambda e: self.show_window_save(e, "lecture")),
                TextButton("Отмена", on_click=lambda e: self.page.show_banner(self.cancel))

            ],
        )
        self.dlg_consultation = AlertDialog(
            title=self.text_date,
            content=Row(
                controls=[
                    self.radio_group
                ]
            ),
            actions=[
                TextButton("Сохранить", on_click=lambda e: self.show_window_save(e, "consultation")),
                TextButton("Отмена", on_click=lambda e: self.page.show_banner(self.cancel))

            ],
        )

    def add_object_practice(self):
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

        self.dlg_practice = AlertDialog(
            title=self.text_date,
            content=Column(
                controls=[
                    self.radio_group,
                    self.radio_group_practice_grade
                ], height=270
            ),
            actions=[
                TextButton("Сохранить", on_click=lambda e: self.show_window_save(e, "practice")),
                TextButton("Отмена", on_click=lambda e: self.page.show_banner(self.cancel))

            ],
        )


class Visible(Table):
    def __init__(self, pageN, id, db, value, today_date):
        super().__init__(pageN, id, db, value, today_date)
        self.page.clean()
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
                            Text("СТАТИСТИКА", size=25),
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
            self.scroll_table_date_lecture,
            self.scroll_table_date_consultation,
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

            self.scroll_table_date_lecture.visible = False
            self.scroll_table_date_consultation.visible = False
        elif selected_index == 1:
            self.scroll_table_lecture.visible = True
            self.scroll_table_date_lecture.visible = True

            self.scroll_table_practice.visible = False
            self.scroll_table_consultation.visible = False

            self.scroll_table_date_consultation.visible = False
        else:
            self.scroll_table_consultation.visible = True
            self.scroll_table_date_consultation.visible = True

            self.scroll_table_lecture.visible = False
            self.scroll_table_practice.visible = False

            self.scroll_table_date_lecture.visible = False
        self.page.update()

# Видимость областей
    def on_segment_change(self, e):
        if e.control.selected_index == 0:  # Cards
            self.scroll_table_practice.visible = False
            self.scroll_table_lecture.visible = False
            self.scroll_table_consultation.visible = False
            self.scroll_table_date_lecture.visible = False
            self.scroll_table_date_consultation.visible = False

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
            self.scroll_table_date_lecture.visible = False
            self.scroll_table_date_consultation.visible = False

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
                    width=270,
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