from tkinter import *
from tkinter import messagebox
from tkcalendar import Calendar
from datetime import date
from datetime import datetime
from textwrap import wrap
from src.Functions import window_to_center


class Visitor():
    def __init__(self, window, connection, cursor, visitor):
        self.wind = window
        self.conn = connection
        self.cursor = cursor
        self.visitor = visitor

        self.free_room = None

        self.tier = None
        self.room = None
        self.visitor_id = []
        self.get_static_info()

        self.cal_begin = Calendar(self.wind, selectmode='day')
        self.cal_end = Calendar(self.wind, selectmode='day')
        self.info_main = Label(text='Выберите даты начала и конца бронирования', height=2)
        self.info_count = Label(text='Вы выбрали бронирование на n д', height=2)
        self.info_sec_l = Label(text='Доступные номера: n')
        self.info_sec_r = Label(text='Инфо:')
        self.box = Listbox(height=15)
        self.scroll = Scrollbar(self.wind, orient=VERTICAL, command=self.box.yview)
        self.box.configure(yscroll=self.scroll.set)
        self.reserve = Label()
        self.empty_space = Label()
        self.conf_res = Button(text='Забронировать', command=self.check_conf, height=2)

        self.place_interface()

        self.check_cal_end()

    def place_interface(self):
        self.info_main.grid(row=0, column=0, sticky=W)
        self.cal_begin.grid(row=1, column=0, sticky=W)
        self.cal_end.grid(row=1, column=2, sticky=E)
        self.info_count.grid(row=2, column=2, sticky=W)
        self.info_sec_l.grid(row=3, column=0, sticky=W)
        self.info_sec_r.grid(row=3, column=2, sticky=W)
        self.box.grid(row=4, column=0, sticky=NSEW)
        self.scroll.grid(row=4, column=1, sticky='ns')
        self.reserve.grid(row=4, column=2, sticky=NSEW)
        self.empty_space.grid(row=5, column=0, sticky=NSEW)
        self.conf_res.grid(row=6, column=0, sticky=NSEW)

        window_to_center(self.wind)

        self.wind.bind('<<CalendarSelected>>', self.check_cal_end)
        self.box.bind('<<ListboxSelect>>', self.check_listbox)

    def check_cal_end(self, event=None):
        mb, db, yb = [int(i) for i in self.cal_begin.get_date().split('/')]
        me, de, ye = [int(i) for i in self.cal_end.get_date().split('/')]
        cal_b = date(int('20' + str(yb)), mb, db)
        cal_e = date(int('20' + str(ye)), me, de)
        cur = datetime.now()
        cal_cur = date(cur.year, cur.month, cur.day)

        if cal_b < cal_cur:
            self.cal_begin.selection_set(cal_cur)
            cal_b = cal_cur
        if cal_b > cal_e:
            self.cal_end.selection_set(cal_b)
            cal_e = cal_b

        cal_dif = (cal_e - cal_b).days + 1
        self.info_count.configure(text=f'Вы выбрали бронирование на {cal_dif} д')

        self.reserve.configure(text='')
        self.update_listbox()

    def update_listbox(self):
        self.box.delete(0, END)

        temp_db = self.cal_begin.get_date().split('/')
        temp_db = '20' + temp_db[2] + '-' + temp_db[0] + '-' + temp_db[1]
        temp_de = self.cal_end.get_date().split('/')
        temp_de = '20' + temp_de[2] + '-' + temp_de[0] + '-' + temp_de[1]

        self.cursor.execute('''SELECT room_id FROM room
                               EXCEPT
                               SELECT room_id FROM reservation
                               WHERE
                                   (check_in_date BETWEEN %s AND %s)
                                   OR
                                   (check_out_date BETWEEN %s AND %s)
                               ORDER BY room_id''', (temp_db, temp_de, temp_db, temp_de))
        self.free_room = [i[0] for i in self.cursor.fetchall()]

        self.info_sec_l.configure(text='Доступные номера: ' + str(len(self.free_room)))

        for i in self.free_room:
            t_id = self.room[i - 1][1] - 1
            self.box.insert(END, '#' + str(self.room[i - 1][0]).ljust(5) +
                            self.tier[t_id][0].ljust(11) + (str(self.tier[t_id][1]) + '₽/день').ljust(13) +
                            str(self.room[i - 1][2]) + ' этаж')

    def check_listbox(self, event=None):
        sel_id = self.free_room[self.box.curselection()[0]]
        sel_room = self.room[sel_id - 1]
        reserve_text = '\n'.join(wrap(self.tier[sel_room[1] - 1][2], 35))
        self.reserve.configure(text=reserve_text)

    def check_conf(self, event=None):
        if len(self.box.curselection()) == 0:
            return

        temp_db = self.cal_begin.get_date().split('/')
        temp_db = '20' + temp_db[2] + '-' + temp_db[0] + '-' + temp_db[1]
        temp_de = self.cal_end.get_date().split('/')
        temp_de = '20' + temp_de[2] + '-' + temp_de[0] + '-' + temp_de[1]

        temp_answ = messagebox.askyesno(title='Подтверждение',
                                        message='Подтвердите бронирование\nc ' + temp_db + ' по ' + temp_de)
        if not temp_answ:
            return

        self.cursor.execute('SELECT get_new_reservation_id()')
        cur_res_id = self.cursor.fetchall()[0][0] + 1
        temp_room_id = self.free_room[self.box.curselection()[0]]
        self.cursor.execute('INSERT INTO reservation VALUES (%s, %s, %s, %s)',
                            (cur_res_id, temp_db, temp_de, temp_room_id))
        for i in self.visitor_id:
            self.cursor.execute('INSERT INTO reservation_visitor VALUES (%s, %s)',
                                (cur_res_id, i))

        cur = datetime.now()
        cal_cur = date(cur.year, cur.month, cur.day)
        self.cal_begin.selection_set(cal_cur)
        self.cal_end.selection_set(cal_cur)
        self.check_cal_end()

        messagebox.showinfo(title='Информация',
                            message='Вы успешно забронировали номер\nc ' + temp_db + ' по ' + temp_de)

    def get_static_info(self):
        self.cursor.execute('SELECT tier_name, price_per_day, description FROM tier')
        self.tier = self.cursor.fetchall()
        self.cursor.execute('SELECT room_number, tier_id, floor_number FROM room ORDER BY room_id')
        self.room = self.cursor.fetchall()
        self.verify_visitor()

    def verify_visitor(self):
        self.cursor.execute('SELECT get_new_visitor_id()')
        temp_cur_id = self.cursor.fetchall()[0][0] + 1
        for i in range(len(self.visitor)):
            self.cursor.execute('''SELECT visitor_id
                                   FROM visitor
                                   WHERE first_name = %s AND second_name = %s
                                   AND birth_date = %s AND sex = %s''',
                                (self.visitor[i][0], self.visitor[i][1],
                                 self.visitor[i][2], self.visitor[i][3]))
            temp_vis_id = self.cursor.fetchall()
            if len(temp_vis_id) == 0:
                self.visitor_id.append(temp_cur_id)
                self.cursor.execute('INSERT INTO visitor VALUES (%s, %s, %s, %s, %s)',
                                    (temp_cur_id, self.visitor[i][0], self.visitor[i][1],
                                     self.visitor[i][2], self.visitor[i][3]))
                temp_cur_id += 1
                print('Гость ' + self.visitor[i][0] + ' ' + self.visitor[i][1] + ' добавлен в базу данных')
            else:
                self.visitor_id.append(temp_vis_id[0][0])
                print('Гость ' + self.visitor[i][0] + ' ' + self.visitor[i][1] + ' уже существует')
