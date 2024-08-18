from tkinter import *
from openpyxl import *


class MyApp:
    def __init__(self, win):
        self.win = win
        self.book = open("file/data.xlsx")
        self.sheet = self.book.worksheets[0]
        self.canvas = Canvas(self.win, height=1200, width=2000, bg="green")
        self.canvas.pack()
        self.entry_login = Entry(self.win, font=("Arial", 40), width=15)
        self.entry_login.place(x=700, y=300)
        self.entry_password = Entry(self.win, font=("Arial", 40), width=15)
        self.entry_password.place(x=700, y=500)
        self.button = Button(self.win, text='Войти', bg='#5bab70', font=("Arial", 30), command=self.check_info)
        self.button.place(x=850, y=700)

    def check_info(self):
        entry_login_password = self.entry_login.get() + self.entry_password.get()
        for row in range(2, self.sheet.max_row + 1):
            data_login_password = str(self.sheet[row][1].value) + str(self.sheet[row][2].value)
            if entry_login_password == data_login_password:
                Groops(self, row)


class Groops:
    def __init__(self, app, row):
        self.app = app
        self.app.entry_login.destroy()
        self.app.entry_password.destroy()
        self.app.button.destroy()
        num_groop = str(self.app.sheet[row][4].value).replace(',', ' ').split()
        y = 200
        self.text_items = []
        for i, text in enumerate(num_groop):
            tag = f"text{i}"
            text_item = self.app.canvas.create_text(940, y, text=f"{text}", font=("Helvetica", 80), fill='white', tags=tag)
            self.text_items.append(text_item)
            self.app.canvas.tag_bind(tag, "<Button-1>", self.on_click)
            y += 200

    def on_click(self, event):
        num_groop = self.app.canvas.itemcget("current", "text")
        Cards(self.app, num_groop, self)

    def delete_text(self):
        for text_item in self.text_items:
            self.app.canvas.delete(text_item)


class Cards:
    def __init__(self, app, num_groop, groops):
        self.app = app
        self.groops = groops
        self.app.entry_login.destroy()
        self.app.entry_password.destroy()
        self.app.button.destroy()
        self.groops.delete_text()
        self.sheet_groop = self.app.book[f'{num_groop}']

        self.app.canvas["bg"] = "white"
        self.text_items = []
        y = 550
        for i in range(1, self.sheet_groop.max_row):
            text_item = self.sheet_groop[i + 1][0].value
            self.text_items.append(text_item)
            text = self.app.canvas.create_text(700, y, text=f"{text_item}", font=("Helvetica", 50), fill="black")
            self.app.canvas.tag_bind(text, "<Button-1>", self.on_text_click)
            y += 200

    def on_text_click(self, event):
        print(self.app.canvas.itemcget("current", "text"))


win = Tk()
win.state('zoomed')
win.title("App")
app = MyApp(win)
win.mainloop()
