import flet as ft

def main(page):
    # Создание колонок таблицы
    columns = [ft.DataColumn(ft.Text(f"Column {i+1}")) for i in range(5)]

    # Значения для смены текста кнопки
    button_texts = ["1", "2", "1у", "2у", ""]

    # Функция для обработки нажатий на кнопки
    def button_click(e):
        # Получение текущего индекса состояния кнопки
        current_text = e.control.text
        next_text = button_texts[(button_texts.index(current_text) + 1) % len(button_texts)]
        e.control.text = next_text
        e.control.update()

    # Создание строк таблицы
    rows = []
    for i in range(5):
        cells = []
        for j in range(5):
            # Установка начального текста кнопки
            cell_content = ft.TextButton(button_texts[0], autofocus=(i == 2 and j == 1), on_click=button_click)
            cell = ft.DataCell(
                ft.Container(
                    content=cell_content,
                    padding=ft.padding.all(10),
                )
            )
            cells.append(cell)
        rows.append(ft.DataRow(cells))

    # Создание таблицы
    table = ft.DataTable(
        columns=columns,
        rows=rows,
        border=ft.border.all(2, "#00FF7F"),
        border_radius=5,
        vertical_lines=ft.BorderSide(2, "black"),
    )

    # Создание кнопок
    button_top = ft.TextButton("Top Button", on_click=lambda e: print("Top button clicked"))
    button_bottom = ft.TextButton("Bottom Button", on_click=lambda e: print("Bottom button clicked"))

    # Добавление элементов на страницу
    page.add(
        ft.Column([
            button_top,
            table,
            button_bottom
        ], alignment=ft.MainAxisAlignment.CENTER)
    )

ft.app(main)
