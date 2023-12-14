from tkinter import *
from src.Application import Application
from src.Login import Login


if __name__ == '__main__':
    login_window = Tk()
    login = Login(login_window)
    login_window.mainloop()

    main_window = Tk()
    application = Application(main_window, login.conn, login.cursor, login.user, login.visitor)
    main_window.mainloop()
