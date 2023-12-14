from tkinter.messagebox import askyesno
from .Visitor import Visitor
from .Admin import Admin


class Application():
    def __init__(self, window, connection, cursor, user, visitor):
        self.wind = window
        self.conn = connection
        self.cursor = cursor
        self.user = user
        self.visitor = visitor

        if self.conn is None or self.cursor is None:
            self.wind.destroy()
            return

        self.wind.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.wind.title('hotel')
        self.wind.resizable(False, False)

        if self.user == 'visitor':
            self.app = Visitor(self.wind, self.conn, self.cursor, self.visitor)
        elif self.user == 'admin':
            self.app = Admin(self.wind, self.conn, self.cursor)
        else:
            self.on_closing()

    def on_closing(self):
        temp_answ = askyesno(title='Подтверждение', message='Выйти?')
        if not temp_answ:
            return
        self.cursor.close()
        self.conn.close()
        print('Курсор и соединение закрыты')
        self.wind.destroy()
