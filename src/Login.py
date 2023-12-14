from tkinter import *
from psycopg2 import connect
from .Functions import window_to_center
from .Functions import check_text
from .Functions import check_date
from .settings.settings import db_params


class Login():
    def __init__(self, window):
        self.conn = None
        self.cursor = None
        self.user = None
        self.visitor = []
        self.wind = window

        self.wind.title('login')
        self.wind.resizable(False, False)

        self.user_login = Button(text='Гость', command=self.num_of_visitors, width=20, height=2)
        self.admin_login = Button(text='Администратор', command=self.admin_connect, width=20, height=2)

        self.user_login.pack()
        self.admin_login.pack()

        window_to_center(self.wind)

        self.vis_num = None
        self.vis_count = 1

        self.inf = None
        self.etr = None

        self.inf_fn = None
        self.inf_sn = None
        self.inf_db = None
        self.inf_sex = None
        self.etr_fn = None
        self.etr_sn = None
        self.etr_db = None
        self.etr_sex_m = None
        self.etr_sex_f = None
        self.s_var = None

        self.conf = None

    def try_connect(self, user, password):
        try:
            self.conn = connect(host=db_params['host'], dbname=db_params['dbname'], user=user, password=password)
            self.conn.autocommit = True
            self.cursor = self.conn.cursor()
            print('Курсор и соединение открыты')
            return True
        except:
            return False

    def num_of_visitors(self):
        self.user = 'visitor'
        self.user_login.destroy()
        self.admin_login.destroy()

        self.inf = Label(text='Введите\nколичество людей,\nкоторые будут проживать\nв одном номере', width=20, height=5)
        self.etr = Entry(width=20)
        self.conf = Button(text='Подтвердить', command=self.check_vis_num, width=20, height=2)

        self.inf.pack()
        self.etr.pack()
        self.conf.pack()
        self.etr.focus()

    def check_vis_num(self):
        self.vis_num = self.etr.get()
        if self.vis_num.isdigit() and 1 <= int(self.vis_num) <= 10:
            self.vis_num = int(self.vis_num)
            self.visitor_connect()
        else:
            self.inf.configure(text='НЕПРАВИЛЬНЫЕ ДАННЫЕ')
            self.etr.delete(0, END)

    def visitor_connect(self):
        self.etr.destroy()
        self.conf.destroy()

        self.inf.configure(text='Гость номер ' + str(self.vis_count), height=2)
        self.inf_fn = Label(text='Введите ваше имя', width=20, height=2)
        self.etr_fn = Entry(width=20)
        self.inf_sn = Label(text='Введите вашу фамилию', width=20, height=2)
        self.etr_sn = Entry(width=20)
        self.inf_db = Label(text='Ваша дата рождения\nФормат: год-месяц-день', width=20, height=3)
        self.etr_db = Entry(width=20)
        self.inf_sex = Label(text='Выберите ваш пол', width=20, height=2)
        self.s_var = StringVar()
        self.s_var.set('N')
        self.etr_sex_m = Radiobutton(text='Мужской', variable=self.s_var, value='M')
        self.etr_sex_f = Radiobutton(text='Женский', variable=self.s_var, value='F')
        self.conf = Button(text='Подтвердить', command=self.check_name, width=20, height=2)

        self.inf_fn.pack()
        self.etr_fn.pack()
        self.inf_sn.pack()
        self.etr_sn.pack()
        self.inf_db.pack()
        self.etr_db.pack()
        self.inf_sex.pack()
        self.etr_sex_m.pack()
        self.etr_sex_f.pack()
        self.conf.pack()
        self.etr_fn.focus()

    def another_visitor(self):
        self.vis_count += 1

        self.inf.configure(text='Гость номер ' + str(self.vis_count))
        self.etr_fn.delete(0, END)
        self.etr_sn.delete(0, END)
        self.etr_db.delete(0, END)
        self.s_var.set('N')

        self.etr_fn.focus()

    def check_name(self):
        self.visitor.append(['', '', '', ''])
        vc = self.vis_count - 1
        self.visitor[vc][0] = self.etr_fn.get()
        self.visitor[vc][1] = self.etr_sn.get()
        self.visitor[vc][2] = self.etr_db.get()
        self.visitor[vc][3] = self.s_var.get()

        flag = True

        if check_text(self.visitor[vc][0]) and len(self.visitor[vc][0]) <= 60:
            self.visitor[vc][0] = self.visitor[vc][0].lower().title()
            self.inf_fn.configure(text='Введите ваше имя', height=2)
        else:
            self.inf_fn.configure(text='НЕПРАВИЛЬНЫЕ ДАННЫЕ\nВведите ваше имя', height=3)
            flag = False

        if check_text(self.visitor[vc][1]) and len(self.visitor[vc][0]) <= 60:
            self.visitor[vc][1] = self.visitor[vc][1].lower().title()
            self.inf_sn.configure(text='Введите вашу фамилию', height=2)
        else:
            self.inf_sn.configure(text='НЕПРАВИЛЬНЫЕ ДАННЫЕ\nВведите вашу фамилию', height=3)
            flag = False

        if check_date(self.visitor[vc][2]):
            self.inf_db.configure(text='Ваша дата рождения\nФормат: год-месяц-день', height=3)
        else:
            self.inf_db.configure(text='НЕПРАВИЛЬНЫЕ ДАННЫЕ\nВаша дата рождения\nФормат: год-месяц-день', height=4)
            flag = False

        if self.visitor[vc][3] != 'N':
            self.inf_sex.configure(text='Выберите ваш пол', height=2)
        else:
            self.inf_sex.configure(text='НЕ ВЫБРАН ПОЛ\nВыберите ваш пол', height=3)
            flag = False

        if flag:
            if self.vis_count < self.vis_num:
                self.another_visitor()
            else:
                if self.try_connect(db_params['visitor'], db_params['visitor_pass']):
                    self.wind.destroy()
                else:
                    self.inf.configure(text='Ошибка входа')
                    self.inf_fn.configure(text='Ошибка входа')
                    self.inf_sn.configure(text='Ошибка входа')
                    self.inf_db.configure(text='Ошибка входа')
                    self.inf_sex.configure(text='Ошибка входа')
                    self.conf.configure(text='Ок', command=self.wind.destroy)
        else:
            self.visitor.pop()

    def admin_connect(self):
        self.user = 'admin'
        self.user_login.destroy()
        self.admin_login.destroy()
        self.inf = Label(text='Введите пароль', width=20, height=2)
        self.etr = Entry(show="*", width=20)
        self.conf = Button(text='Войти', command=self.check_pass, width=20, height=2)

        self.inf.pack()
        self.etr.pack()
        self.conf.pack()
        self.etr.focus()

    def check_pass(self):
        if self.try_connect(db_params['admin'], self.etr.get()):
            self.wind.destroy()
        else:
            self.inf.configure(text='Ошибка входа')
            self.etr.delete(0, END)
