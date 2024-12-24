from flet import *
import datetime
import xlsxwriter
import os
import threading

from Admins import Admins
from Databases import Databases
from Teachers import Teachers
from Statement import Statement
from Excel import Excel
from Student import Student
from Mail import Mail


class SplashScreen:
    def __init__(self, page):
        self.page = page
        self.page.title = "BNTU"
        self.page.theme_mode = 'light'
        self.timer_thread = None
        self.is_running = True  # Флаг для отслеживания состояния приложения
        self.page.on_close = self.stop_timers  # Привязываем остановку таймеров к закрытию программы
        self.start_timer()
        self.draw_graphics()

    def start_timer(self):
        # Основной таймер на 60 секунд
        self.timer_thread = threading.Timer(60, self.close_application)
        self.timer_thread.start()

        # Таймер на 10 секунд до завершения для предупреждения
        threading.Timer(50, self.show_ten_seconds_warning).start()

    def stop_timers(self, _=None):
        # Остановка всех таймеров при закрытии окна
        self.is_running = False  # Устанавливаем флаг, что приложение закрывается
        if self.timer_thread and self.timer_thread.is_alive():
            self.timer_thread.cancel()
        print("Таймер остановлен.")

    def show_ten_seconds_warning(self):
        # Проверяем, активно ли приложение перед показом диалога
        if not self.is_running:
            return

        # Открытие диалогового окна за 10 секунд до завершения таймера
        self.dialog = AlertDialog(
            title=Text("AFK"),
            content=Text("Через 10 секунд окно закроется!"),
            actions=[
                TextButton("Продолжить", on_click=self.close_dialog)  # Кнопка закрытия уведомления
            ]
        )
        self.page.dialog = self.dialog
        self.dialog.open = True
        self.page.update()

    def close_dialog(self, e):
        # Закрытие диалогового окна (но приложение продолжает отсчет времени)
        if not self.is_running:
            return
        self.dialog.open = False
        self.page.update()

    def draw_graphics(self):
        self.button_go = ElevatedButton(text="Далее", width=300, height=50, bgcolor="#2196F3",
                                           color='black', on_click=lambda _: self.stop_timer_and_proceed())
        self.dialog = AlertDialog(
            title=Text("AFK"),
            content=Text("Через 10 секунд окно закроется!"),
            actions=[
                TextButton("Продолжить", on_click=self.page.close_banner())  # Кнопка закрытия
            ]
        )

        self.page.add(
        Container(
            content=Column(
                [
                    Text(value="Белорусский национальный технический университет", weight=FontWeight.BOLD, size=20),
                    Text(value="Факультет информационных технологий и робототехники", weight=FontWeight.BOLD, size=20),
                    Text(value="Кафедра программного обеспечения информационных систем и технологий", weight=FontWeight.BOLD, size=20)
                ],
                alignment=MainAxisAlignment.CENTER,
                horizontal_alignment=CrossAxisAlignment.CENTER,
                spacing=1
            ),
            padding=padding.only(left=250)
        )
    )
        self.page.add(
            Column(
                [
                    Container(Text(value="Курсовой проект", weight=FontWeight.BOLD, size=26),
                                 padding=padding.only(top=80), alignment=alignment.center),
                    Text(value="по дисциплине  Языки программирования", weight=FontWeight.BOLD, size=14)
                ],
                alignment=MainAxisAlignment.CENTER,
                horizontal_alignment=CrossAxisAlignment.CENTER,
                spacing=2
            )
        )
        self.page.add(Row([Text(value='Приложение "Контроль успеваемости студентов"'
                                      , weight=FontWeight.BOLD, size=22)], alignment=MainAxisAlignment.CENTER))
        self.page.add(
            Row(
                [
                    Container(
                        Image(src=os.path.join(os.path.dirname(os.path.abspath(__file__)), "img/logo.jpg")),
                        alignment=alignment.center_left,
                        padding=padding.only(left=70),
                        expand=True
                    ),
                    Container(
                        Column(
                            [
                                Column([
                                    Text(value='Выполнил: Студент группы 10701123', size=17),
                                    Text(value='Нелипович Евгений Григорьевич', size=17)],
                                    spacing=0),  # Блок с фамилией студента
                                Container(
                                    Column([
                                        Text(value='Преподаватель: к.ф.-м.н., доц.', size=17),
                                        Text(value='Сидорик Валерий Владимирович', size=17)],
                                        spacing=0),  # Блок с фамилией преподавателя
                                    padding=padding.only(right=23),
                                )
                            ],
                            spacing=25,
                            horizontal_alignment=CrossAxisAlignment.END
                        ),
                        alignment=alignment.center_right,
                    )
                ],
                alignment=MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=CrossAxisAlignment.CENTER
            )
        )
        self.page.add(
            Column(
                [
                    Container(
                        Row(
                            [Text(value='Минск, 2024', size=20)],
                            alignment=MainAxisAlignment.CENTER
                        ),
                        padding=padding.only(top=15),
                        alignment=alignment.center
                    )
                ],
                horizontal_alignment=CrossAxisAlignment.CENTER
            )
        )
        self.page.add(
            Row(
                [
                    self.button_go,
                ],
                alignment=MainAxisAlignment.SPACE_BETWEEN,
            )
        )
        self.page.update()

    def close_application(self):
        # Проверяем, активно ли приложение перед завершением
        if not self.is_running:
            return
        self.page.window_close()

    def stop_timer_and_proceed(self):
        # Остановка таймера и переход к следующему экрану
        self.stop_timers()
        Main(self.page)  # Переход к следующему экрану


class Main:
    def __init__(self, pageM):
        self.page = pageM
        self.db = Databases()
        self.page.title = "BNTU"
        self.page.clean()
        self.page.update()
        self.page.vertical_alignment = MainAxisAlignment.CENTER
        self.page.window_maximized = True

        if self.check_auto() is None:
            for i in self.db.get_info_select_from("email", "teachers WHERE name='admin'"):
                self.email = i

            # виджеты
            self.user_login = TextField(value="", width=300, text_align=TextAlign.LEFT, label="Логин", height=100,
                                        on_change=self.validate)
            self.user_password = TextField(value="", width=300, text_align=TextAlign.LEFT, label="Пароль",
                                           password=True,
                                           can_reveal_password=True, height=80, on_change=self.validate)
            self.btn_entry = ElevatedButton(text="Войти", disabled=True, width=300, height=50, bgcolor='#B0E0E6',
                                            color='black', on_click=lambda _: self.check_users())
            self.check_box = CupertinoCheckbox(label="Запомнить меня")

            # верхний бар
            self.page.appbar = AppBar(
                leading_width=20,
                title=Text("БНТУ | BNTU"),
                bgcolor=colors.SURFACE_VARIANT,
                actions=[
                    IconButton(icons.SUNNY, on_click=self.change_topic),
                    PopupMenuButton(
                        items=[
                            PopupMenuItem(text="Об авторе", on_click=lambda _: self.autor_app(1)),
                            PopupMenuItem(text="Об приложении", on_click=lambda _: self.autor_app(2)),
                            PopupMenuItem(text="Тех. поддержка", on_click=lambda _: self.page.show_banner(
                                AlertDialog(
                                    title=Text("Тех. поддержка"),
                                    content=Text(f"Ко всем вопросам пишите на почту\n{self.email[0]}", size=25),
                                    actions=[
                                        TextButton("Отмена", on_click=lambda e: self.page.close_banner()),
                                    ]
                                )
                            )),
                            PopupMenuItem(text="Выход", on_click=lambda _: self.page.window_close()),
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
                            self.check_box,
                            self.btn_entry,
                        ])
                    ], alignment=MainAxisAlignment.CENTER
                )
            )

# переход по темам
    def change_topic(self, e):
        if self.page.theme_mode == "light":
            self.page.theme_mode = 'dark'
        else:
            self.page.theme_mode = 'light'
        self.page.update()

# проверка, было что-то написано в логине и пароле
    def validate(self, e):
        if all([self.user_login.value, self.user_password.value]):
            self.btn_entry.disabled = False
        else:
            self.btn_entry.disabled = True
        self.page.update()

# проверка на вход
    def check_users(self):
        for i in self.db.get_info_select_from("rowid, login, password, name", "teachers"):
            if (f'{self.user_login.value}', f'{self.user_password.value}') == (i[1], i[2]):
                self.page.show_banner(SnackBar(Text(f"Успешный вход", size=20)))
                self.page.clean()
                if self.check_box.value:
                    self.db.set_info_update("teachers", "new_check='1'", f"rowid='{i[0]}'")
                if i[0] == 1:
                    self.page.appbar = AppBar(
                        leading_width=20,
                        title=Text(f"БНТУ | BNTU   {i[3]}"),
                        bgcolor=colors.SURFACE_VARIANT,
                        actions=[
                            IconButton(icons.SETTINGS, on_click=lambda _: SettingsAdmin(self.page, self.db, i[0])),
                            IconButton(icons.SUNNY, on_click=self.change_topic),
                            PopupMenuButton(
                                items=[
                                    PopupMenuItem(text="Тех. поддержка", on_click=lambda _: self.page.show_banner(
                    AlertDialog(
                        title=Text("Тех. поддержка"),
                        content=Text(f"Ко всем вопросам пишите на почту\n{self.email[0]}", size=25),
                        actions=[
                            TextButton("Отмена", on_click=lambda e: self.page.close_banner()),
                        ]
                    )
                )),
                                    PopupMenuItem(text="Выход из аккаунта", on_click=lambda _: self.leave_acc(i[0]))
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
                                    PopupMenuItem(text="Аккаунт", on_click=lambda _: AccountTeachers(self.page, i[3], i[0], self.db)),
                                    PopupMenuItem(text="Выход из аккаунта", on_click=lambda _: self.leave_acc(i[0]))
                                ]
                            ),
                            IconButton(icons.SUNNY, on_click=self.change_topic),
                            PopupMenuButton(
                                items=[
                                    PopupMenuItem(text="Настройки", on_click=lambda e: Settings(self.page, i[0], self.db)),
                                    PopupMenuItem(text="Тех. поддержка", on_click=lambda _: self.page.show_banner(
                    AlertDialog(
                        title=Text("Тех. поддержка"),
                        content=Text(f"Ко всем вопросам пишите на почту\n{self.email[0]}", size=25),
                        actions=[
                            TextButton("Отмена", on_click=lambda e: self.page.close_banner()),
                        ]
                    )
                )),
                                ]
                            ),
                        ],
                    )
                    self.page.update()
                    Numbers(self.page, i[0], self.db)
            else:
                self.page.show_banner(SnackBar(Text(f"Неверные данные", size=20)))

    def autor_app(self, value):
        text = Text(size=20)
        img = Image()
        if value == 1:
            text.value = "Нелипович Евгений Григорьевич\n10701123\nzhenya.nelipovich@gmail.com"
            img.src = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img/i.jpg")
        else:
            img.src = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img/logo.jpg")
            text.value = ("Программа 'Контроль успеваемости'\n"
                          "предназначена для мониторинга и анализа академических результатов учащихся.\n "
                          "Она помогает учителям отслеживать прогресс в обучении, выявлять слабые и сильные стороны,\n "
                          "а также планировать дальнейшую учебную деятельность.")

        self.page.show_banner(AlertDialog(
            content=Column([
                img,
                text
            ], alignment=alignment.center),
            actions=[
                TextButton("Отмена", on_click=lambda e: self.page.close_banner()),
            ]
        ))

    def check_auto(self):
        for i in self.db.get_info_select_from("rowid, login, password, name", "teachers WHERE new_check='1'"):
            if i[0] == 1:
                self.page.clean()
                self.page.appbar = AppBar(
                    leading_width=20,
                    title=Text(f"БНТУ | BNTU   {i[3]}"),
                    bgcolor=colors.SURFACE_VARIANT,
                    actions=[
                        IconButton(icons.SETTINGS, on_click=lambda _: SettingsAdmin(self.page, self.db, i[0])),
                        IconButton(icons.SUNNY, on_click=self.change_topic),
                        PopupMenuButton(
                            items=[
                                PopupMenuItem(text="Тех. поддержка", on_click=lambda _: self.page.show_banner(
                                    AlertDialog(
                                        title=Text("Тех. поддержка"),
                                        content=Text(f"По всем вопросам пишите на почту\n{self.email[0]}", size=25),
                                        actions=[
                                            TextButton("Отмена", on_click=lambda e: self.page.close_banner()),
                                        ]
                                    )
                                )),
                                PopupMenuItem(text="Выход из аккаунта", on_click=lambda _: self.leave_acc(i[0]))
                            ]
                        ),
                    ],
                )
                self.page.update()
                Admin(self.page, self.db)
                return 1
            else:
                self.page.appbar = AppBar(
                    leading_width=20,
                    title=Text(f"БНТУ | BNTU   {i[3]}"),
                    bgcolor=colors.SURFACE_VARIANT,
                    actions=[
                        PopupMenuButton(
                            icon=icons.ACCOUNT_CIRCLE_OUTLINED,
                            items=[
                                PopupMenuItem(text="Аккаунт",
                                              on_click=lambda _: AccountTeachers(self.page, i[3], i[0], self.db)),
                                PopupMenuItem(text="Выход из аккаунта", on_click=lambda _: self.leave_acc(i[0]))
                            ]
                        ),
                        IconButton(icons.SUNNY, on_click=self.change_topic),
                        PopupMenuButton(
                            items=[
                                PopupMenuItem(text="Настройки", on_click=lambda e: Settings(self.page, i[0], self.db)),
                                PopupMenuItem(text="Тех. поддержка", on_click=lambda _: self.page.show_banner(
                                    AlertDialog(
                                        title=Text("Тех. поддержка"),
                                        content=Text(f"По всем вопросам пишите на почту\nzhenya.nelipovich@gmail.com", size=25),
                                        actions=[
                                            TextButton("Отмена", on_click=lambda e: self.page.close_banner()),
                                        ]
                                    )
                                )),
                            ]
                        ),
                    ],
                )
                self.page.update()
                Numbers(self.page, i[0], self.db)
                return 1

    def leave_acc(self, id):
        self.db.set_info_update("teachers", "new_check='0'", f"rowid='{id}'")
        Main(self.page)


class Numbers:
    def __init__(self, pageN, id, db):
        self.mail_con = None
        self.choice_types = None
        self.comment = None
        self.mail = None
        self.name = None
        self.scroll_container = None
        self.page = pageN
        self.id = id
        self.db = db
        self.teacher = Teachers()
        self.statement = Statement()
        self.mail = Mail()

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
                            on_click=lambda e: self.next_class(selected_value['value'], 2)
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
                            Text("Выберите группу:", size=25, color="black"),
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
                            on_click=lambda e: self.next_class(selected_number_ref.current.value, 2)
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
                self.page.show_banner(
                    AlertDialog(
                        title=Text("Выберите опцию"),
                        content=Container(
                            Row([
                                ElevatedButton(text="ОТПРАВИТЬ",
                                               height=50,
                                               on_click=lambda _: self.next_class(value, 1)),
                                ElevatedButton(text="ТАБЛИЦА",
                                               height=50,
                                               on_click=lambda _: self.next_class(value, 2)),
                            ])
                        ),
                        actions=[
                            TextButton("Отмена", on_click=lambda e: self.page.close_banner()),
                        ]
                    )
                )

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

    def next_class(self, value, choice):
        self.page.close_banner()
        if choice == 2:
            Visible(self.page, self.id, self.db, value, self.statement.get_today_date())
        else:
            self.scroll_container = ListView(width=700, height=500)
            self.name = TextField(
                value=f"{self.teacher.get_str(self.db.get_info_select_from("name", f"teachers WHERE rowid='{self.id}'"))}",
                width=700, text_align=TextAlign.LEFT, label="От кого", height=100)
            self.mail_con = TextField(value="@gmail.com", width=700, text_align=TextAlign.LEFT, label="Почта(получателя)", height=100)
            self.comment = TextField(value="", width=700, text_align=TextAlign.LEFT, label="Комментарий(необязательно)",
                                     height=100)

            self.choice_types = RadioGroup(
                content=Row([
                    Radio(value="practice", label="Практика"),
                    Radio(value="lecture", label="Лекция"),
                    Radio(value="consultation", label="Консультация"),
                ]),
                value="practice",
            )

            self.scroll_container.controls.append(
                Column([
                    self.name,
                    self.mail_con,
                    self.comment,
                    self.choice_types,
                ])
            )
            self.page.show_banner(
                AlertDialog(
                    title=Text("ОТПРАВИТЬ"),
                    content=self.scroll_container,
                    actions=[
                        TextButton("Отмена", on_click=lambda e: self.page.close_banner()),
                        TextButton("Отправить", on_click=lambda e: self.create_excel_file(value, self.choice_types.value)),
                    ]
                )
            )

    def create_excel_file(self, group, types):
        # Извлечение данных из базы данных
        names = self.teacher.get_list_name(self.db.get_info_select_from("name", f"group{group}"))
        dates = list(set(self.teacher.get_list_name(
            self.db.get_info_select_from("dates", f"date_{group} WHERE type='{types}'"))))
        dates.sort()  # Сортировка дат

        if types != "practice":
            data = self.db.get_info_select_from("name, date, value", f"statement_{types}{group}")
            # Преобразование data в удобный формат
            data_dict = {(item[0], item[1]): item[2] for item in data}
        else:
            data = self.db.get_info_select_from("name, date, value, subgroup", f"statement_{types}{group}")
            # Преобразование data в удобный формат
            data_dict = {(item[0], item[1]): f"{item[2]}|{item[3]}" for item in data}

        # Создание Excel-файла
        filename = f"statement_{group}_{types}.xlsx"
        filepath = os.path.join(os.getcwd(), "file", filename)
        workbook = xlsxwriter.Workbook(filepath)
        worksheet = workbook.add_worksheet()

        # Заполнение заголовка с датами (строка 0, начиная со столбца 1)
        for col, date in enumerate(dates, start=1):
            worksheet.write(0, col, date)

        # Заполнение имен (столбец 0, начиная со строки 1)
        for row, name in enumerate(names, start=1):
            worksheet.write(row, 0, name)

        # Заполнение значений для каждой строки и каждого столбца
        for row, name in enumerate(names, start=1):
            for col, date in enumerate(dates, start=1):
                value = data_dict.get((name, date), None)
                if value is not None:
                    worksheet.write(row, col, value)

        workbook.close()
        print()
        # Отправка файла по электронной почте с динамическим путем
        self.mail.send_email("Ведомость", self.comment.value, self.mail_con.value, filepath)


class Settings(Numbers):
    def __init__(self, pageN, id, db):
        super().__init__(pageN, id, db)
        self.radio_groups = None
        self.radio_groups_table = None
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
                        on_click=lambda e: self.show_content(),
                        border_radius=15,
                        border=border.all(5, "green")
                    ),
                    Container(
                        Text("ТАБЛИЦА", size=70, style=TextStyle(letter_spacing=30)),
                        width=1500,
                        height=130,
                        alignment=alignment.center,
                        on_click=lambda e: self.show_content_table(),
                        border_radius=15,
                        border=border.all(5, "green")
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
                    Radio(value="0", label="1", tooltip="Комбобокс"),
                ]),
                on_change=handle_radio_change
            ),
            RadioGroup(
                value=self.settings_value[0],
                content=Row([
                    Radio(value="1", label="2", tooltip="Прокрутка"),
                ]),
                on_change=handle_radio_change
            ),
            RadioGroup(
                value=self.settings_value[0],
                content=Row([
                    Radio(value="2", label="3", tooltip="Контейнеры"),
                ]),
                on_change=handle_radio_change
            )
        ]

        # Добавляем радио-группы в колонки
        scroll_cont.controls.append(Column(controls=[
            Row([Image(src=os.path.join(os.path.dirname(os.path.abspath(__file__)), "img/number_3.png")), self.radio_groups[0]]),
            Row([Image(src=os.path.join(os.path.dirname(os.path.abspath(__file__)), "img/number_2.png")), self.radio_groups[1]]),
            Row([Image(src=os.path.join(os.path.dirname(os.path.abspath(__file__)), "img/number_1.png")), self.radio_groups[2]]),
        ]))

        dialog = AlertDialog(
            title=Text("Выберите опцию"),
            content=scroll_cont,
            actions=[
                TextButton("Отмена", on_click=lambda e: self.page.close_banner()),
                TextButton("Сохранить", on_click=lambda e: self.save_selection(1))
            ]
        )
        self.page.show_banner(dialog)

    def show_content_table(self):
        def handle_radio_change(e):
            selected_value = e.control.value
            for control in self.radio_groups_table:
                control.value = selected_value
            self.page.update()

        scroll_cont = ListView(width=800)
        self.radio_groups_table = [
            RadioGroup(
                value=self.settings_value[1],
                content=Row([
                    Radio(value="0", label="1", tooltip="Диалоговое окно"),
                ]),
                on_change=handle_radio_change
            ),
            RadioGroup(
                value=self.settings_value[1],
                content=Row([
                    Radio(value="1", label="2", tooltip="При помощи пробелов"),
                ]),
                on_change=handle_radio_change
            ),
        ]

        # Добавляем радио-группы в колонки
        scroll_cont.controls.append(Column(controls=[
            Row([Image(src=os.path.join(os.path.dirname(os.path.abspath(__file__)), "img/table_1.png")), self.radio_groups_table[0]]),
            Row([Image(src=os.path.join(os.path.dirname(os.path.abspath(__file__)), "img/table_2.png")), self.radio_groups_table[1]]),
        ]))

        dialog = AlertDialog(
            title=Text("Выберите опцию"),
            content=scroll_cont,
            actions=[
                TextButton("Отмена", on_click=lambda e: self.page.close_banner()),
                TextButton("Сохранить", on_click=lambda e: self.save_selection(2))
            ]
        )
        self.page.show_banner(dialog)

    def save_selection(self, types):
        if types == 1:
            selected_value = None
            for control in self.radio_groups:
                if control.value:
                    selected_value = control.value
                    continue
            self.settings_value = f"{selected_value}" + f"{self.settings_value[1]}"
        else:
            selected_value_table = None
            for control in self.radio_groups_table:
                if control.value:
                    selected_value_table = control.value
                    continue
            self.settings_value = self.settings_value[0] + f"{selected_value_table}"
        self.db.set_info_update("teachers", f"settings='{self.settings_value}'", f"rowid='{self.id}'")
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
        self.student = Student()

        self.now = datetime.datetime.now()
        self.settings_value = self.teacher.get_str(
            self.db.get_info_select_from("settings", f"teachers WHERE rowid='{self.id}'"))

        self.grade_texts = [".", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
        self.performance_texts = [".", "1", "2", "1y", "2y"]
        self.statistics = ["Номер", "Имя", "Средний бал",
                           "Успеваемость на практике(был/всего)",
                           "Успеваемость на лекции(был/всего)", "Успеваемость на консультации(был/всего)"]

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

        # всплывающее окна

        self.save = SnackBar(Text(f"Успешно", size=20))

        self.error_date = SnackBar(Text(f"Такая дата уже есть", size=20))

        self.banner = SnackBar(Text(f"Сперва добавьте дату", size=20))

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
        self.add_student_but = ElevatedButton(text="Добавить студента",
                                              width=300,
                                              height=50,
                                              bgcolor='#B0E0E6',
                                              color='black',
                                              on_click=lambda _: AddStudent(self.page, self.db, self.value, self.id),
                                              visible=False)
        self.add_file_but = ElevatedButton(text="Добавить студентов через Excel",
                                           width=300,
                                           height=50,
                                           bgcolor='#B0E0E6',
                                           color='black',
                                           on_click=lambda _: ExcelFile(self.page, self.db, self.value, self.id),
                                           visible=False)

    def delete_student(self, group, condition):
        self.db.delete_student(group, condition)
        self.scroll_card.controls.clear()
        self.create_card()
        self.page.close_banner()
        self.page.update()

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
                                                  on_click=lambda _, name=self.list_name[i]:
                                                  AccountStudent(self.page, self.db, self.value, self.id, name, 1)),
                                    PopupMenuItem(text="Изменить",
                                                  on_click=lambda _, name=self.list_name[i]:
                                                  EditStudent(self.page, self.db, name, self.value, self.id)),
                                    PopupMenuItem(text="Удалить", on_click=lambda _, name=self.list_name[i]:
                                    self.page.show_banner(
                                        AlertDialog(
                                            title=Text("Подтверждение", size=40),
                                            content=Container(
                                                content=Column(
                                                    [
                                                        Text("Вы точно уверены, что хотите удалить?", size=20)
                                                    ]
                                                ),
                                                height=50  # Задайте желаемую ширину здесь
                                            ),
                                            actions=[
                                                TextButton(
                                                    content=Text("Отмена", size=20),
                                                    on_click=lambda _: self.page.close_banner()
                                                ),
                                                TextButton(
                                                    content=Text("Да", size=20),
                                                    on_click=lambda _: self.delete_student(f"{self.value}", f"name='{name}'")
                                                ),
                                            ],
                                        )
                                    )
                                    ),
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

        self.sort_asc = True
        self.scroll_table_date_lecture = ListView(width=1700, height=60)
        self.scroll_table_lecture = ListView(expand=1, width=1700)
        self.scroll_table_date_consultation = ListView(width=1700, height=60, visible=False)
        self.scroll_table_consultation = ListView(expand=1, width=1700, visible=False)
        self.scroll_table_practice = ListView(expand=1, spacing=10, padding=15, width=1700, visible=False)

        self.now_dates_lecture = self.date_lecture
        self.now_dates_consultation = self.date_consultation
        self.now_dates_practice_1 = self.date_practice_1
        self.now_dates_practice_2 = self.date_practice_2
        self.mode = None
        self.focus_row = 0
        self.focus_col = 1
        self.choice_focus_practice = 1
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
        self.columns_table_statistics = None
        self.rows_table_statistics = None
        self.kol_lecture = 0
        self.kol_consultation = 0
        self.kol_practice_1 = 0
        self.kol_practice_2 = 0

        self.add_object_lecture_consultation()
        self.add_object_practice()

        self.create_table_lecture(self.date_lecture, self.week_list_lecture, self.list_name)
        self.create_table_consultation(self.date_consultation, self.week_list_consultation, self.list_name)
        self.create_table_practice(self.date_practice_1, self.date_practice_2, self.list_subgroup_1, self.list_subgroup_2)

    def create_table_lecture(self, list_date, list_week, list_name):
        # Таблица с датами ЛЕКЦИЯ
        columns_table_lecture_date = [DataColumn(Text(f"{list_date[i]}", color="black", size=25)) for i in range(6)]

        table_lecture_date = DataTable(
            width=1279,
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
            ]), padding=padding.only(120, 0, 0, 0)
        )
        self.scroll_table_date_lecture.controls.append(container_table_lecture_date)

        # Таблица основная ЛЕКЦИЯ
        self.columns_table_lecture = [
            DataColumn(Text("Номер", color="black", size=15)),
            DataColumn(Text("Имя", color="black", size=15), on_sort=lambda _: self.sort_by_name("lecture", list_name, list_week, list_date, "None", "None"))
        ]
        for i in range(2, 8):
            self.columns_table_lecture.append(DataColumn(Text(f"{list_week[i - 2]}", color="black", size=15)))

        self.row_table_lecture = [
            DataRow([
                DataCell(
                    Container(
                        content=TextButton(
                            content=Text(
                                f"{i + 1}" if j == 0 else f"{list_name[i]}" if j == 1 else f"{self.statement.check_which_value(
                                    self.db.get_info_join(f"{list_name[i]}", f"{list_date[j - 2]}",
                                                          f"{self.value}", "lecture"))}", size=20, color="black"),
                            on_click=lambda e, n=j, a=i: self.put_grade_student(list_date[n - 2], list_name[a],
                                                                                "lecture", a, n,
                                                                                3) if n != 1 and n != 0 else None,
                            autofocus=(i == self.focus_row and j == self.focus_col),
                            width=100 if j == 0 else 190 if j == 1 else 150, height=40,
                            on_long_press=lambda e, n=j, row_index=i: self.handle_row_double_tap(row_index, "lecture",
                                                                                                 "None") if n == 1 else None),
                        width=100 if j == 0 else 205 if j == 1 else None,
                        alignment=alignment.center
                    ),
                )
                for j in range(8)
            ], )
            for i in range(len(list_name))
        ]

        table_lecture = DataTable(
            width=1000,
            bgcolor="white",
            border=border.all(2, "#00FF7F"),
            border_radius=5,
            vertical_lines=BorderSide(2, "black"),
            columns=self.columns_table_lecture,
            rows=self.row_table_lecture,
        )

        self.scroll_table_lecture.controls.append(table_lecture)

    def sort_by_name(self, types, list_name, list_week, list_date, list_date_2, list_name_2):
        """ Сортировка по столбцу Имя """
        list_name.sort(reverse=not self.sort_asc)
        self.sort_asc = not self.sort_asc

        if types == "lecture":
            self.scroll_table_lecture.controls.clear()
            self.scroll_table_date_lecture.controls.clear()

            self.calculation_lecture()

            self.create_table_lecture(list_date, list_week, list_name)
        elif types == "consultation":
            self.scroll_table_consultation.controls.clear()
            self.scroll_table_date_consultation.controls.clear()

            self.calculation_consultation()

            self.create_table_consultation(list_date, list_week, list_name)
        else:
            self.scroll_table_practice.controls.clear()

            self.calculation_practice()
            list_name_2.sort(reverse=not self.sort_asc)
            self.create_table_practice(list_date, list_date_2, list_name, list_name_2)
        self.page.update()

    def create_table_consultation(self, list_date, list_week, list_name):
        # Таблица с датами КОНСУЛЬТАЦИЯ
        column_table_consultation_date = [DataColumn(Text(f"{list_date[i]}", color="black", size=25))
                                          for i in range(6)]

        table_consultation_date = DataTable(
            width=1278,
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
            ]), padding=padding.only(122, 0, 0, 0),
        )

        self.scroll_table_date_consultation.controls.append(container_table_consultation_date)

        # таблица основная КОНСУЛЬТАЦИЯ
        self.column_consultation = [
            DataColumn(Text("Номер", color="black", size=15)),
            DataColumn(Text("Имя", color="black", size=15), on_sort=lambda _: self.sort_by_name("consultation", list_name, list_week, list_date, "None", "None"))
        ]
        for i in range(2, 8):
            self.column_consultation.append(DataColumn(Text(f"{list_week[i - 2]}", color="black", size=15)))
        self.rows_consultation = [  # i - строки | j - столбцы
            DataRow([
                DataCell(
                    Container(
                        content=TextButton(
                            content=Text(f"{i+1}" if j == 0 else f"{list_name[i]}" if j == 1 else f"{self.statement.check_which_value(
                                self.db.get_info_join(f"{list_name[i]}", f"{list_date[j - 2]}",
                                                  f"{self.value}", "consultation"))}", size=20, color="black"),
                            on_click=lambda e, n=j, a=i: self.put_grade_student(list_date[n - 2], list_name[a], "consultation", a, n, 3) if n != 1 and n != 0 else None,
                            autofocus=(i == self.focus_row and j == self.focus_col), width=100 if j == 0 else 190 if j == 1 else 150, height=40,
                            on_long_press=lambda e, n=j, row_index=i: self.handle_row_double_tap(row_index, "consultation", "None") if n == 1 else None),
                        width=100 if j == 0 else 205 if j == 1 else None,
                        alignment=alignment.center
                    ),
                )
                for j in range(8)
            ])
            for i in range(len(list_name))
        ]

        table_consultation = DataTable(
            width=1000,
            bgcolor="white",
            border=border.all(2, "#061CF9"),
            border_radius=5,
            vertical_lines=BorderSide(2, "black"),
            columns=self.column_consultation,
            rows=self.rows_consultation,
        )

        self.scroll_table_consultation.controls.append(table_consultation)

    def create_table_practice(self, list_date_1, list_date_2, list_subgroup_1, list_subgroup_2):
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
            ] + ([self.mode] if self.settings_value[1] == "1" else []))
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
            DataColumn(Text("Номер", color="black", size=15)),
            DataColumn(Text("Имя", color="black", size=15), on_sort=lambda _: self.sort_by_name("practice", list_subgroup_1, "None", list_date_1, list_date_2, list_subgroup_2))
        ]
        for i in range(2, 8):
            self.column_practice.append(DataColumn(Text(f"{list_date_1[i - 2]}", color="black", size=15)))

        self.rows_practice = [  # i - строки | j - столбцы
            DataRow([
                DataCell(
                    Container(
                        content=TextButton(
                            content=Text(f"{i+1}" if j == 0 else f"{list_subgroup_1[i]}" if j == 1 else f"{self.statement.check_which_value_practice(
                                self.db.get_info_select_from("subgroup, value", 
                                                             f"statement_practice{self.value} WHERE "
                                                                                f"name='{list_subgroup_1[i]}'"
                                                                                f" AND date='{list_date_1[j - 2]}'"))}",
                                         size=20, color="black"),
                            on_click=lambda e, n=j, a=i: self.put_grade_student(list_date_1[n - 2], list_subgroup_1[a], "practice", a, n, 1) if n != 0 and n != 1 else None,
                            autofocus=(i == self.focus_row and j == self.focus_col) if self.choice_focus_practice == 1 else None, width=100 if j == 0 else 190 if j == 1 else 150, height=40,
                            on_long_press=lambda e, n=j, row_index=i: self.handle_row_double_tap(row_index, "practice", "1") if n == 1 else None),
                        width=100 if j == 0 else 205 if j == 1 else None, alignment=alignment.center),
                )
                for j in range(8)
            ])
            for i in range(len(list_subgroup_1))
        ]

        table_practice_1 = DataTable(
            width=1000,
            bgcolor="white",
            border=border.all(2, "#F90606"),
            border_radius=5,
            vertical_lines=BorderSide(2, "black"),
            columns=self.column_practice,
            rows=self.rows_practice,
        )

        # таблица 2
        self.column_practice_2 = [
            DataColumn(Text("Номер", color="black", size=15)),
            DataColumn(Text("Имя", color="black", size=15), on_sort=lambda _: self.sort_by_name("practice", list_subgroup_1, "None", list_date_1, list_date_2, list_subgroup_2))
        ]
        for i in range(2, 8):
            self.column_practice_2.append(DataColumn(Text(f"{list_date_2[i - 2]}", color="black", size=15)))
        self.rows_practice_2 = [  # i - строки | j - столбцы
            DataRow([
                DataCell(
                    Container(
                        content=TextButton(
                            content=Text(f"{i+1}" if j == 0 else f"{list_subgroup_2[i]}" if j == 1 else f"{self.statement.check_which_value_practice(
                                self.db.get_info_select_from("subgroup, value", 
                                                             f"statement_practice{self.value} WHERE "
                                                                                f"name='{list_subgroup_2[i]}'"
                                                                                f" AND date='{list_date_2[j - 2]}'"))}",
                                         size=20, color="black"),
                            on_click=lambda e, n=j, a=i: self.put_grade_student(list_date_2[n - 2], list_subgroup_2[a], "practice", a, n, 2) if n != 0 and n != 1 else None,
                            autofocus=(i == self.focus_row and j == self.focus_col), width=100 if j == 0 else 190 if j == 1 else 150, height=40,
                            on_long_press=lambda e, n=j, row_index=i: self.handle_row_double_tap(row_index, "practice", "2") if n == 1 else None,),
                        width=100 if j == 0 else 205 if j == 1 else None, alignment=alignment.center),
                )
                for j in range(8)
            ])
            for i in range(len(list_subgroup_2))
        ]

        table_practice_2 = DataTable(
            width=1000,
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
                                       on_click=lambda e: Subgroup(self.page, self.id, self.db, self.value, self.date)))
        self.scroll_table_practice.controls.append(container_2)
        self.scroll_table_practice.controls.append(table_practice_2)

    def handle_row_double_tap(self, row_index, types, subgroup):
        row = None
        if types == "lecture":
            row = self.row_table_lecture
        elif types == "consultation":
            row = self.rows_consultation
        elif types == "statistics":
            row = self.rows_table_statistics
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
                    on_dismiss=lambda e: self.page.close_banner()
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
            self.page.close_banner()
            self.update_table(f"{types}")

        con = Container(content=Column(controls=[]), alignment=alignment.center)
        len_list = len(type_list)
        for i in range(len_list):
            if type_list[i] != "                 ":
                con.content.controls.append(
                    TextButton(
                        content=Text(f"{type_list[i]}", size=30),
                        on_click=lambda e, a=i: self.page.show_banner(
    AlertDialog(
        title=Text("Подтверждение", size=40),
        content=Container(
            content=Column(
                [
                    Text("Вы точно уверены, что хотите удалить дату?", size=20)
                ]
            ),
            height=50  # Задайте желаемую ширину здесь
        ),
        actions=[
            TextButton(
                content=Text("Отмена", size=20),
                on_click=lambda _: self.page.close_banner()
            ),
            TextButton(
                content=Text("Да", size=20),
                on_click=lambda _: delete(e, types, subgroup, type_list[a])
            ),
        ],
    )
)
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
                        on_click=lambda _: self.page.close_banner()
                    ),

                ],
            )
        )

    def update_table_click(self, types, list_date, list_date_2):
        new_week_list = self.statement.get_list_week(list_date)
        if types == "lecture":
            self.scroll_table_lecture.controls.clear()
            self.scroll_table_date_lecture.controls.clear()

            self.create_table_lecture(list_date, new_week_list, self.list_name)
        elif types == "consultation":
            self.scroll_table_consultation.controls.clear()
            self.scroll_table_date_consultation.controls.clear()

            self.create_table_consultation(list_date, new_week_list, self.list_name)
        else:
            self.scroll_table_practice.controls.clear()

            self.create_table_practice(list_date, list_date_2, self.list_subgroup_1, self.list_subgroup_2)
        self.page.update()

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

    def put_grade_student(self, date, name, types, row, col, choice):
        self.focus_row = row
        self.focus_col = col

        value_t = self.statement.check_which_value(self.db.get_info_join(f"{name}", f"{date}",
                                                                         f"{self.value}", f"{types}"))

        value_g = self.statement.check_which_value(self.db.get_info_select_from("subgroup",
                                                                                f"statement_practice{self.value} "
                                                                                f"WHERE name='{name}' "
                                                                                f"AND date='{date}'"))

        if choice == 1:
            self.choice_focus_practice = 1
        elif choice == 2:
            self.choice_focus_practice = 2

        if date == "                 ":
            self.page.show_banner(self.banner)
        elif self.settings_value[1] == "1":
            if types == "practice":
                if self.mode.value == "grades":
                    value_g = self.grade_texts[
                        (self.grade_texts.index(value_g) + 1) % len(self.grade_texts)
                        ]
                else:
                    value_t = self.performance_texts[
                        (self.performance_texts.index(value_t) + 1) % len(self.performance_texts)
                        ]
                self.show_window_save_2(types, name, date, value_t, value_g)
            elif types == "lecture" or types == "consultation":
                value_t = self.performance_texts[
                    (self.performance_texts.index(value_t) + 1) % len(self.performance_texts)
                    ]
                self.show_window_save_2(types, name, date, value_t, value_g)
        else:
            self.radio_group.value = value_t  # значение для radio button
            if types == "practice":
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
            if self.radio_group.value != ".":
                self.db.insert_info_values(f"statement_{types}{self.value}", f"'{name}', '{date}', "
                                                                             f"'{self.radio_group.value}'")
        else:
            if self.radio_group.value != "." or self.radio_group_practice_grade.value != ".":
                self.db.insert_info_values(f"statement_{types}{self.value}", f"'{name}', '{date}', "
                                                                              f"'{self.radio_group.value}', "
                                                                              f"'{self.radio_group_practice_grade.value}'")

        self.page.close_banner()
        if types == "lecture":
            self.update_table_click(f"{types}", self.now_dates_lecture, "None")
        elif types == "consultation":
            self.update_table_click(f"{types}", self.now_dates_consultation, "None")
        else:
            self.update_table_click(f"{types}", self.now_dates_practice_1, self.now_dates_practice_2)

    def show_window_save_2(self, types, name, date, value_performance, value_grades):
        self.db.delete_info_statement(f"{name}", f"{date}", f"{self.value}", f"{types}")
        if types != "practice":
            self.db.insert_info_values(f"statement_{types}{self.value}", f"'{name}', '{date}', "
                                                                             f"'{value_performance}'")
        else:
            self.db.insert_info_values(f"statement_{types}{self.value}", f"'{name}', '{date}', "
                                                                              f"'{value_performance}', "
                                                                              f"'{value_grades}'")

        self.page.close_banner()
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
                self.now_dates_lecture = new_date_list
                self.update_table_parameter(new_date_list, types, "None")
            elif types == "consultation":
                new_date_list, new_const_list = check_data_left(self.kol_consultation, list_type)
                self.kol_consultation = new_const_list
                self.now_dates_consultation = new_date_list
                self.update_table_parameter(new_date_list, types, "None")
            else:
                if subgroup == "1":
                    new_date_list, new_const_list = check_data_left(self.kol_practice_1, self.date_practice_1)
                    self.kol_practice_1 = new_const_list
                    self.now_dates_practice_1 = new_date_list
                    self.update_table_parameter(new_date_list, types, list_type_2)
                else:
                    new_date_list, new_const_list = check_data_left(self.kol_practice_2, self.date_practice_2)
                    self.kol_practice_2 = new_const_list
                    self.now_dates_practice_2 = new_date_list
                    self.update_table_parameter(list_type, types, new_date_list)
        else:
            if types == "lecture":
                new_date_list, new_const_list = check_data_right(self.kol_lecture, list_type)
                if new_const_list is not None:
                    self.kol_lecture = new_const_list
                    self.now_dates_lecture = new_date_list
                    self.update_table_parameter(new_date_list, types, "None")
            elif types == "consultation":
                new_date_list, new_const_list = check_data_right(self.kol_consultation, list_type)
                if new_const_list is not None:
                    self.kol_consultation = new_const_list
                    self.now_dates_consultation = new_date_list
                    self.update_table_parameter(new_date_list, types, "None")
            else:
                if subgroup == "1":
                    new_date_list, new_const_list = check_data_right(self.kol_practice_1, self.date_practice_1)
                    if new_const_list is not None:
                        self.kol_practice_1 = new_const_list
                        self.now_dates_practice_1 = new_date_list
                        self.update_table_parameter(new_date_list, types, list_type_2)
                else:
                    new_date_list, new_const_list = check_data_right(self.kol_practice_2, self.date_practice_2)
                    if new_const_list is not None:
                        self.kol_practice_2 = new_const_list
                        self.now_dates_practice_2 = new_date_list
                        self.update_table_parameter(list_type, types, new_date_list)

    def add_object_lecture_consultation(self):
        # radio button
        self.radio_group = RadioGroup(content=Row([
            Radio(value="1", label="1", tooltip="1 час пропуска"),
            Radio(value="2", label="2", tooltip="2 часа пропуска"),
            Radio(value="1y", label="1y", tooltip="1 час (уважительно)"),
            Radio(value="2y", label="2y", tooltip="2 часа (уважительно)"),
            Radio(value=".", label="Пусто", tooltip="Очистить поле")
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
                TextButton("Отмена", on_click=lambda e: self.page.close_banner())

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
                TextButton("Отмена", on_click=lambda e: self.page.close_banner())

            ],
        )

    def add_object_practice(self):
        self.mode = RadioGroup(
            content=Row([
                Radio(value="grades", label="Оценки",),
                Radio(value="performance", label="Успеваемость"),
            ]),
            value="performance",
        )
        self.radio_group_practice_grade = RadioGroup(content=Container(
            Column([
                Text("Оценка:", size=20),
                Row([
                    Radio(value="1", label="1"),
                    Radio(value="2", label="2"),
                    Radio(value="3", label="3"),
                    Radio(value="4", label="4"),
                    Radio(value="5", label="5"),
                ]),
                Row([
                    Radio(value="6", label="6"),
                    Radio(value="7", label="7"),
                    Radio(value="8", label="8"),
                    Radio(value="9", label="9"),
                    Radio(value="10", label="10"),
                ]),
                Radio(value=".", label="Пусто")
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
                TextButton("Отмена", on_click=lambda _: self.page.close_banner())

            ],
        )


class Statistics(Table):
    def __init__(self, pageN, id, db, value, today_date):
        super().__init__(pageN, id, db, value, today_date)

        self.scroll_table_statistics = ListView(expand=1, width=1700, visible=False)
        self.sort_st = True
        self.create_table_statistics(self.list_name)

    def create_table_statistics(self, list_name):
        self.columns_table_statistics = [
            DataColumn(Text(f"{self.statistics[i]}", color="black", size=15), on_sort=lambda _: self.sort_by_name_statistics(list_name)) for i in range(6)]
        self.rows_table_statistics = [  # i - строки | j - столбцы
            DataRow([
                DataCell(
                    Container(
                        content=TextButton(
                            content=Text(f"{i+1}" if j == 0 else f"{list_name[i]}" if j == 1 else f"{self.student.get_statistics_grade(
                                self.db.get_info_select_from("subgroup", 
                                                             f"statement_practice{self.value} WHERE name='{list_name[i]}'"
                                                             ))}"
                            if j == 2 else f"{self.student.get_statistics_progress(
                                self.db.get_info_select_from("value", 
                                                             f"statement_practice{self.value} WHERE name='{list_name[i]}'"
                                                             ),
                                self.date_practice_1 if list_name[i] in self.list_subgroup_1 else self.date_practice_2 if list_name[i] in self.list_subgroup_2 else None)}"
                            if j == 3 else f"{self.student.get_statistics_progress(
                                self.db.get_info_select_from("value", 
                                                             f"statement_lecture{self.value} WHERE name='{list_name[i]}'"
                                                             ), 
                                self.date_lecture)}"
                            if j == 4 else f"{self.student.get_statistics_progress(
                                self.db.get_info_select_from("value", 
                                                             f"statement_consultation{self.value} WHERE name='{list_name[i]}'"
                                                             ), 
                                self.date_consultation)}",
                                         size=20, color="black"),
                            width=100 if j == 0 else 190 if j == 1 else 190, height=40,
                            on_long_press=lambda e, n=j, row_index=i: self.handle_row_double_tap(row_index, "statistics", "None") if n == 1 else None),
                        width=100 if j == 0 else None,
                        alignment=alignment.center
                    ),
                )
                for j in range(7)
            ], )
            for i in range(len(list_name))
        ]

        table_statistics = DataTable(
            width=1000,
            bgcolor="white",
            border=border.all(2, "yellow"),
            border_radius=5,
            vertical_lines=BorderSide(2, "black"),
            columns=self.columns_table_statistics,
            rows=self.rows_table_statistics,
        )
        self.scroll_table_statistics.controls.append(table_statistics)

    def sort_by_name_statistics(self, list_name):
        list_name.sort(reverse=not self.sort_st)
        self.sort_st = not self.sort_st

        self.scroll_table_statistics.controls.clear()
        self.create_table_statistics(list_name)
        self.page.update()


class Visible(Statistics):
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
                    IconButton(icons.ARROW_BACK, on_click=lambda _: Numbers(self.page, self.id, self.db), tooltip="Назад"),
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
                    IconButton(icons.REFRESH, on_click=lambda _: Visible(self.page, self.id, self.db, self.value, 1), tooltip="Обновить"),
                    IconButton(icons.MENU_BOOK_ROUNDED, on_click=lambda _: self.guide(),
                               tooltip="Руководство"),
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
            self.scroll_table_statistics
        )
        self.page.add(self.choice_mini)

# Видимость областей мини
    def choice_table(self, e):
        self.focus_row = 0
        self.focus_col = 1
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
            self.scroll_table_statistics.visible = False
        elif e.control.selected_index == 1:  # Table
            self.scroll_card.visible = False
            self.add_student_but.visible = False
            self.add_file_but.visible = False
            self.choice_mini.visible = True
            self.scroll_table_statistics.visible = False
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

            self.scroll_table_statistics.visible = True
        self.page.update()

    def guide(self):
        scroll_container = ListView(width=900, height=900)
        scroll_container.controls.append(
            Container(
                Column([
                    Row([
                        Image(src=os.path.join(os.path.dirname(os.path.abspath(__file__)), "img/guide_1.png")),
                        Text("Можно долгим нажатием на имя\nвыделить поле", size=20)
                    ]),
                    Text("Если какие-то данные в таблице не обновились, то нажмите кнопку 'Обновить'", size=20),
                    Text("В настройках можно изменить способ выставление оценок", size=20),
                    Row([
                        Image(src=os.path.join(os.path.dirname(os.path.abspath(__file__)), "img/guide_2.png")),
                        Text("Можно сортировать нажав на колонку (с датами не работает)", size=20)
                    ]),
                ])
            )
        )
        self.page.show_banner(
            AlertDialog(
                title=Text("Руководство"),
                content=scroll_container,
                actions=[
                    TextButton("Понятно", on_click=self.page.close_banner())
                ]
            )
        )


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
                            Text("ГРУППЫ", size=25),
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
                                                  self.page.show_banner(
                                                      AlertDialog(
                                                          title=Text("Подтверждение", size=40),
                                                          content=Container(
                                                              content=Column(
                                                                  [
                                                                      Text("Вы точно уверены, что хотите удалить?",
                                                                           size=20)
                                                                  ]
                                                              ),
                                                              height=50  # Задайте желаемую ширину здесь
                                                          ),
                                                          actions=[
                                                              TextButton(
                                                                  content=Text("Отмена", size=20),
                                                                  on_click=lambda _: self.page.close_banner()
                                                              ),
                                                              TextButton(
                                                                  content=Text("Да", size=20),
                                                                  on_click=lambda _: self.delete_teacher("teachers", f"name='{name}'")
                                                              ),
                                                          ],
                                                      )
                                                  )
                                                  ),
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
                                                  self.page.show_banner(
                                                      AlertDialog(
                                                          title=Text("Подтверждение", size=40),
                                                          content=Container(
                                                              content=Column(
                                                                  [
                                                                      Text("Вы точно уверены, что хотите удалить?",
                                                                           size=20)
                                                                  ]
                                                              ),
                                                              height=50  # Задайте желаемую ширину здесь
                                                          ),
                                                          actions=[
                                                              TextButton(
                                                                  content=Text("Отмена", size=20),
                                                                  on_click=lambda _: self.page.close_banner()
                                                              ),
                                                              TextButton(
                                                                  content=Text("Да", size=20),
                                                                  on_click=lambda _: self.delete_table(number)
                                                              ),
                                                          ],
                                                      )
                                                  )
                                                  )
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
        self.page.close_banner()
        Admin(self.page, self.db)

    def delete_teacher(self, table, condition):
        self.db.delete_teachers(table, condition)
        self.page.close_banner()
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
                    IconButton(icons.ARROW_BACK, on_click=lambda _: Admin(self.page, self.db)),
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
                                    AccountStudent(self.page, self.db, self.group, 0, name, 1)),
                                    PopupMenuItem(text="Изменить",
                                                  on_click=lambda _, name=self.list_name[i]: lambda _: EditStudent(self.page, self.db, name, self.group, 0)),
                                    PopupMenuItem(text="Удалить",
                                                  on_click=lambda _, name=self.list_name[i]:
                                                  self.page.show_banner(
                                                      AlertDialog(
                                                          title=Text("Подтверждение", size=40),
                                                          content=Container(
                                                              content=Column(
                                                                  [
                                                                      Text("Вы точно уверены, что хотите удалить?",
                                                                           size=20)
                                                                  ]
                                                              ),
                                                              height=50  # Задайте желаемую ширину здесь
                                                          ),
                                                          actions=[
                                                              TextButton(
                                                                  content=Text("Отмена", size=20),
                                                                  on_click=lambda _: self.page.close_banner()
                                                              ),
                                                              TextButton(
                                                                  content=Text("Да", size=20),
                                                                  on_click=lambda _: self.delete_student(f"{self.group}", f"name='{name}'")
                                                              ),
                                                          ],
                                                      )
                                                  )
                                                  )
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
                                              bgcolor='#B0E0E6', color='black', on_click=lambda _: AddStudent(self.page, self.db, self.group, 0))
        self.add_file_but = ElevatedButton(text="Добавить данные через Excel", width=300, height=50,
                                           bgcolor='#B0E0E6', color='black', on_click=lambda _: ExcelFile(self.page, self.db, self.group, 0))
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
        self.page.close_banner()
        AdminGroup(self.page, self.db, self.group)


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

        self.dlg = SnackBar(Text(f"Успешно", size=20))

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

        self.dlg = SnackBar(Text(f"Успешно", size=20))

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

        self.dlg = SnackBar(Text(f"Успешно", size=20))

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
                self.db.create_table(f"date_{self.text_num_group.value}", "dates text, type text, subgroup text")
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

        self.dlg = SnackBar(Text(f"Успешно", size=20))

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
                    self.db.insert_info_values("teachers", f"'{self.text_name.value}', "
                                                           f"'{self.text_login.value}', "
                                                           f"'{self.text_password.value}', "
                                                           f"'{self.text_items.value}', "
                                                           f"'{self.text_num_group.value}', "
                                                           f"'None', '00', '0'")
                    self.text_name.value = ''
                    self.text_login.value = ''
                    self.text_password.value = ''
                    self.text_items.value = ''
                    self.text_num_group.value = ''
                    self.page.update()
            except:
                self.error_write_num.value = ("ОШИБКА, в поле Группы нужно записывать через запятую и"
                                             " с одним пробелом после f{}")
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

        self.dlg = SnackBar(Text(f"Успешно", size=20))

        self.error = SnackBar(Text(f"ОШИБКА", size=20))

# кнопка назад
    def click_end(self, e):
        self.page.clean()
        if self.id == 0:
            AdminGroup(self.page, self.db, self.group)
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

        self.dlg = SnackBar(Text(f"Успешно", size=20))

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

        self.dlg = SnackBar(Text(f"Успешно", size=20))

# кнопка назад
    def click_end(self, e):
        self.page.clean()
        if self.id == 0:
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


class ExcelFile:
    def __init__(self, pageA, dbA, number, id):
        self.page = pageA
        self.db = dbA
        self.group = number
        self.id = id
        self.excel = Excel()

        self.page.clean()
        self.page.horizontal_alignment = CrossAxisAlignment.CENTER
        self.page.vertical_alignment = MainAxisAlignment.CENTER
        self.page.update()

        # FilePicker для выбора файла
        self.file_picker = FilePicker(on_result=self.transformation_excel_db)
        self.page.overlay.append(self.file_picker)
        self.choice = RadioGroup(
            content=Column([
                Radio(value="all", label="Удалить все прошлые записи"),
                Radio(value="add", label="Добавить уже к существующим записям"),
            ]),
            value="all",
        )
        # Кнопка для открытия FilePicker
        self.page.add(
            Container(Column([
                Text("Пример как должны располагаться файлы:", color="red", size=20),
                Image(src="img/excel_1.png"),
                self.choice,
                Row([
                    ElevatedButton(
                        text="Назад",
                        icon=icons.EXIT_TO_APP,
                        on_click=self.go_back
                    ),
                    ElevatedButton(
                        text="Загрузить файл",
                        icon=icons.FILE_OPEN,
                        on_click=self.open_excel_file
                    ),
                ], alignment=alignment.center)
            ]), width=450, alignment=alignment.center, padding=75, border=border.all(1, "black"), border_radius=15),
        )

    def transformation_excel_db(self, e):
        name_list_excel = []
        if self.file_picker.result is not None and self.file_picker.result.files:  # проверка на то что файл был выбран и нажат
            name_list_excel = self.excel.get_list_name(self.file_picker.result.files[0].path)
            if self.choice.value == "all":
                self.db.delete_all_value_table(f"group{self.group}")
            for i in name_list_excel:
                self.db.insert_info_values(f"group{self.group}", f"'{i}', 'None'")

    def open_excel_file(self, e):
        self.file_picker.pick_files(
            allowed_extensions=["xlsx", "xls"],  # Только Excel-файлы
            allow_multiple=False,
        )

    def go_back(self, e):
        if self.id == 0:
            AdminGroup(self.page, self.db, self.group)
        else:
            Visible(self.page, self.id, self.db, self.group, 1)


class AccountStudent(Info):
    def __init__(self, pageN, db, value, id, name, today_date):
        super().__init__(pageN, id, db, value, today_date)
        self.id = id
        self.name = name
        self.student = Student()
        self.statement = Statement()
        self.teacher = Teachers()

        self.page.clean()
        self.page.update()

        self.red_radius_practice = None
        self.red_radius_lecture = None
        self.red_radius_consultation = None

        self.scroll = ListView(expand=1, width=1700)
        self.red_radius_lecture = self.definition_percent(self.date_lecture, "lecture")
        self.red_radius_consultation = self.definition_percent(self.date_consultation, "consultation")
        self.red_radius_practice = self.definition_percent(self.date_practice_2 if
                    self.teacher.get_str(self.db.get_info_select_from("subgroup", f"group{self.value} WHERE name='{self.name}'")) == "2" else
                    self.date_practice_1 if
                    self.teacher.get_str(self.db.get_info_select_from("subgroup", f"group{self.value} WHERE name='{self.name}'")) == "1" else
                    [0, 0], "practice")
        self.create_scroll_box()
        self.page.add(
            Row([
                IconButton(icons.ARROW_BACK, on_click=lambda _: self.go_back()),
            ], alignment=alignment.top_left),
            self.scroll
        )

    def create_chart(self, dates, types):
        kol_date = dates.count("                 ")
        # соответствующие значения оси X для данных точек
        data_points_x = [2 + 3 * i for i in range(len(dates) - kol_date)]

        value_point = []

        for i in range(len(data_points_x)):
            value = self.teacher.get_str(self.db.get_info_select_from("value", f"statement_{types}{self.value} WHERE date='{dates[i]}' AND name='{self.name}'"))

            if value == "2y":
                value_point.append(2)
            elif value == "1y":
                value_point.append(1)
            elif value == "":
                value_point.append(0)
            elif value == ".":
                value_point.append(0)
            else:
                value_point.append(value)

        data_values = [(data_points_x[i], value_point[i]) for i in range(len(data_points_x))]

        # Создаем данные для LineChartData на основе списка значений
        data_points = [
            LineChartDataPoint(x, y) for x, y in data_values
        ]

        data_1 = [
            LineChartData(
                data_points=data_points,
                color=colors.PINK,
                stroke_width=8,
            ),
        ]

        bottom_axis_labels = [
            ChartAxisLabel(
                value=data_points_x[i],
                label=Container(
                    Text(
                        dates[i],
                        size=15,
                        weight=FontWeight.BOLD,
                        color=colors.with_opacity(0.5, colors.BLACK),
                    ),
                    margin=margin.only(top=10),
                ),
            )
            for i in range(len(data_points_x))
        ]

        # Находим максимальный X
        max_x = max(x for x, y in data_values)

        chart = LineChart(
            data_series=data_1,
            border=Border(
                bottom=BorderSide(1, colors.with_opacity(0.5, colors.ON_SURFACE))
            ),
            bottom_axis=ChartAxis(
                labels=bottom_axis_labels,
                labels_size=100,
            ),
            tooltip_bgcolor=colors.with_opacity(0.8, colors.BLACK),
            min_y=0,
            max_y=2,
            min_x=0,
            max_x=max_x,
        )

        return chart

    def definition_percent(self, dates, types):
        kol_space = dates.count("                 ")
        full_dates = len(dates)-kol_space
        was_not_couple = 0
        for i in range(full_dates):
            value = self.teacher.get_str(self.db.get_info_select_from("value", f"statement_{types}{self.value} WHERE name='{self.name}' AND date='{dates[i]}'"))
            if value == "2" or value == "2y" or value == "1" or value == "1y":
                was_not_couple += 1
        try:
            return 100 * was_not_couple // full_dates
        except:
            return 0

    def create_scroll_box(self):
        scroll = Column([
            Container(
                Column([
                    Text(self.name, color="black", size=75),
                    Text(f"          {self.value}", color="black", size=50)
                ]), alignment=alignment.center, bgcolor="#e8e8e8", border_radius=15
            ),
            Container(
                Row([
                    Container(
                        Column([
                            self.create_chart_circle(self.red_radius_practice, 100-self.red_radius_practice),
                            Text("Практика", color="black", size=25)
                        ], alignment=alignment.center),
                        bgcolor="#c5c5c5",
                        width=250,
                        height=250,
                        alignment=alignment.center,
                        border_radius=5
                    ),
                    Container(
                        Column([
                            self.create_chart_circle(self.red_radius_lecture, 100-self.red_radius_lecture),
                            Text("Лекция", color="black", size=25)
                        ], alignment=alignment.center),
                        bgcolor="#c5c5c5",
                        width=250,
                        height=250,
                        alignment=alignment.center,
                        border_radius=5
                    ),
                    Container(
                        Column([
                            self.create_chart_circle(self.red_radius_consultation, 100-self.red_radius_consultation),
                            Text("Консультация", color="black", size=25)
                        ], alignment=alignment.center),
                        bgcolor="#c5c5c5",
                        width=250,
                        height=250,
                        alignment=alignment.center,
                        border_radius=5
                    ),
                ], alignment=alignment.center),
                alignment=alignment.center, bgcolor="#e8e8e8",
                border_radius=15,
                padding=padding.only(470, 0, 0, 0),
            ),
            Container(
                Column([
                    self.create_chart(self.date_lecture, "lecture"),
                    Text("Лекция", color="black", size=25),
                ]), alignment=alignment.center, bgcolor="#e8e8e8", border_radius=15, height=400, padding=50
            ),
            Container(
                Column([
                    self.create_chart(self.date_practice_2, "practice") if
                    self.teacher.get_str(self.db.get_info_select_from("subgroup", f"group{self.value} WHERE name='{self.name}'")) == "2" else
                    self.create_chart(self.date_practice_1, "practice") if
                    self.teacher.get_str(self.db.get_info_select_from("subgroup", f"group{self.value} WHERE name='{self.name}'")) == "1" else
                    Text("НЕТУ ПОДГРУППЫ", color="red", size=100),
                    Text("Практика(посещаемость)", color="black", size=25),
                ]), alignment=alignment.center, bgcolor="#e8e8e8", border_radius=15, height=400, padding=50
            ),
            Container(
                Column([
                    self.create_chart(self.date_consultation, "consultation"),
                    Text("Консультация", color="black", size=25),
                ]), alignment=alignment.center, bgcolor="#e8e8e8", border_radius=15, height=400, padding=50
            ),
        ])
        self.scroll.controls.append(scroll)

    def create_chart_circle(self, value1, value2):
        normal_radius = 50
        hover_radius = 60
        normal_title_style = TextStyle(
            size=16, color=colors.WHITE, weight=FontWeight.BOLD
        )
        hover_title_style = TextStyle(
            size=22,
            color=colors.WHITE,
            weight=FontWeight.BOLD,
            shadow=BoxShadow(blur_radius=2, color=colors.BLACK54),
        )

        def on_chart_event(e: PieChartEvent):
            for idx, section in enumerate(e.control.sections):
                if idx == e.section_index:
                    section.radius = hover_radius
                    section.title_style = hover_title_style
                else:
                    section.radius = normal_radius
                    section.title_style = normal_title_style
            e.control.update()

        def create_pie_chart(value1, value2):
            chart = PieChart(
                sections=[
                    PieChartSection(
                        value1,
                        title=f"{value1}%",
                        title_style=normal_title_style,
                        color=colors.RED,
                        radius=normal_radius,
                    ),
                    PieChartSection(
                        value2,
                        title=f"{value2}%",
                        title_style=normal_title_style,
                        color=colors.GREEN,
                        radius=normal_radius,
                    ),
                ],
                sections_space=0,
                center_space_radius=40,
                on_chart_event=on_chart_event,
                expand=True,
            )
            return chart

        return create_pie_chart(value1, value2)

    def go_back(self):
        if self.id == 0:
            AdminGroup(self.page, self.db, self.value)
        else:
            Visible(self.page, self.id, self.db, self.value, 1)


def main(page: Page):
    page.theme_mode = 'light'
    SplashScreen(page)


app(target=main)