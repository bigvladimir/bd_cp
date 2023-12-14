from tkinter import *
from tkinter.ttk import Treeview
from tkinter.messagebox import showinfo
from src.Functions import window_to_center
from src.Functions import check_date


class Admin():
    def __init__(self, window, connection, cursor):
        self.wind = window
        self.conn = connection
        self.cursor = cursor

        self.cur_tabn = None
        self.cur_coln = None

        self.table_name = None
        self.col_name = {}
        self.get_static_info()

        self.add_table_buttons()
        self.table_wid = None
        self.scroll = None
        self.add_empty_table()

        window_to_center(self.wind)

    def add_table_buttons(self):
        row_count = 0
        if len(self.table_name) <= 14:
            h = 2
        else:
            h = 1

        for i in range(len(self.table_name)):
            Button(text=self.table_name[i], command=lambda x=self.table_name[i]: self.get_table(x),
                   width=14, height=h).grid(row=i, column=0)
            row_count += 1
        if row_count < 14:
            for i in range(row_count, 14):
                Label(height=2).grid(row=i, column=0)

        Button(text='Добавить строку', command=self.tab_new_line).grid(row=15, column=1, sticky=NSEW)

    def add_empty_table(self):
        self.table_wid = Treeview(self.wind, columns=[0, 1, 2, 3], show='headings', height=28)
        self.table_wid.column(0, width=80)
        self.table_wid.grid(row=0, column=1, rowspan=14, sticky=NSEW)
        self.scroll = Scrollbar(self.wind, orient=VERTICAL, command=self.table_wid.yview)
        self.table_wid.configure(yscroll=self.scroll.set)
        self.scroll.grid(row=0, column=2, rowspan=14, sticky=NS)

    def tab_edit(self, event=None):
        temp_val = self.table_wid.item(self.table_wid.selection()[0])['values']
        temp_etr = []

        top = Toplevel(self.wind)

        top.title('Редактирование')
        top.resizable(False, False)

        Label(top, text='Столбец', width=14).grid(row=0, column=0)
        Label(top, text='Текущее значение', width=14).grid(row=1, column=0)
        Label(top, text='Новое значение', width=14).grid(row=2, column=0)
        for i in range(len(self.cur_coln)):
            Label(top, text=self.cur_coln[i][0], width=14).grid(row=0, column=i+1)
            Label(top, text=temp_val[0], width=14).grid(row=1, column=i+1)
            temp_etr.append(Entry(top, width=14))
            temp_etr[i].grid(row=2, column=i+1)
        Label(top).grid(row=3, column=0)
        Button(top, text='Обновить', command=lambda x=top, y=temp_val, z=temp_etr: self.tab_upt(x, y, z), width=14).grid(row=4, column=0)
        Button(top, text='Отмена', command=top.destroy, width=13).grid(row=4, column=1)
        Button(top, text='Удалить', command=lambda x=top, y=temp_val: self.tab_del(x, y), width=13).grid(row=4, column=2)

        top.geometry("+%d+%d" % (self.wind.winfo_x()+150, self.wind.winfo_y()+200))
        top.transient(self.wind)
        top.grab_set()
        top.focus_set()
        top.wait_window()

        self.get_table(self.cur_tabn)

    def check_etr(self, etrs):
        temp_answ = ''
        for i in range(len(etrs)):
            if len(etrs[i]) == 0:
                continue
            tp_n = self.cur_coln[i][0]
            tp = self.cur_coln[i][1]
            tp_l = self.cur_coln[i][2]
            if tp == 'integer':
                if not etrs[i].isdigit():
                    temp_answ += f'{tp_n}: неправильная запись числа\n'
                elif int(etrs[i]) <= 0:
                    temp_answ += f'{tp_n}: неположительное число\n'
            elif tp == 'date':
                if not check_date(etrs[i]):
                    temp_answ += f'{tp_n}: некорректная дата\n'
            elif tp == 'character varying':
                if len(etrs[i]) > tp_l:
                    temp_answ += f'{tp_n}: слишком длинный текст\n'
            elif tp == 'character':
                if len(etrs[i]) > tp_l:
                    temp_answ += f'{tp_n}: не символ\n'
                elif tp_n == 'sex' and etrs[i] not in 'MF':
                    temp_answ += f'{tp_n}: неправильный пол\n'
        return temp_answ

    def tab_upt(self, window, v_id, etrs):
        str_etrs = []
        for i in etrs:
            str_etrs.append(i.get())
        window.destroy()
        str_len_check = False
        for i in str_etrs:
            if len(i) > 0:
                str_len_check = True
                break
        if not str_len_check:
            showinfo(title='Инфо', message='Не предоставлена\nинформация')
            return
        temp_answ = self.check_etr(str_etrs)
        if len(temp_answ) == 0:
            try:
                q1 = f'UPDATE {self.cur_tabn}\nSET '
                q2 = '\nWHERE '
                flag = False
                for i in range(len(etrs)):
                    if len(str_etrs[i]) > 0:
                        if flag:
                            q1 += ', '
                        if self.cur_coln[i][1] == 'integer':
                            q1 += f'{self.cur_coln[i][0]} = {str_etrs[i]}'
                        else:
                            q1 += f'{self.cur_coln[i][0]} = \'{str_etrs[i]}\''
                        flag = True
                    if i > 0:
                        q2 += ' AND '
                    q2 += f'{self.cur_coln[i][0]} = %s'
                self.cursor.execute(q1 + q2, v_id)
                showinfo(title='Инфо', message='Обновление прошло успешно')
            except:
                showinfo(title='Инфо', message='Невозможно обновить,\nмешает связь id\nс другими таблицами')
        else:
            showinfo(title='Инфо', message=temp_answ)

    def tab_del(self, window, v_id):
        window.destroy()
        try:
            q = f'DELETE FROM {self.cur_tabn}\nWHERE '
            for i in range(len(v_id)):
                if i > 0:
                    q += ' AND '
                q += f'{self.cur_coln[i][0]} = %s'
            self.cursor.execute(q, v_id)
            showinfo(title='Инфо', message='Удаление прошло успешно')
        except:
            showinfo(title='Инфо', message='Невозможно удалить,\nмешает связь\nс другими таблицами')

    def tab_new_line(self):
        if self.cur_tabn is None:
            return

        temp_etr = []

        top = Toplevel(self.wind)

        top.title('Добавление строки')
        top.resizable(False, False)

        Label(top, text='Столбец', width=14).grid(row=0, column=0)
        Label(top, text='Значение', width=14).grid(row=1, column=0)
        for i in range(len(self.cur_coln)):
            Label(top, text=self.cur_coln[i][0], width=14).grid(row=0, column=i + 1)
            temp_etr.append(Entry(top, width=14))
            temp_etr[i].grid(row=1, column=i + 1)
        Label(top).grid(row=2, column=0)
        Button(top, text='Добавить', command=lambda x=top, y=temp_etr: self.tab_add(x, y), width=14).grid(row=4, column=0)
        Button(top, text='Отмена', command=top.destroy, width=13).grid(row=4, column=1)

        top.geometry("+%d+%d" % (self.wind.winfo_x() + 150, self.wind.winfo_y() + 200))
        top.transient(self.wind)
        top.grab_set()
        top.focus_set()
        top.wait_window()

        self.get_table(self.cur_tabn)

    def tab_add(self, window, etrs):
        str_etrs = []
        for i in etrs:
            str_etrs.append(i.get())
        window.destroy()
        for i in str_etrs:
            if len(i) == 0:
                showinfo(title='Инфо', message='Предоставлена неполная\nинформация')
                return
        temp_answ = self.check_etr(str_etrs)
        if len(temp_answ) == 0:
            try:
                q = f'INSERT INTO {self.cur_tabn}\nVALUES ('
                for i in range(len(etrs)):
                    if self.cur_coln[i][1] == 'integer':
                        str_etrs[i] = int(str_etrs[i])
                    if i > 0:
                        q += ', '
                    q += '%s'
                q += ')'
                self.cursor.execute(q, str_etrs)
                showinfo(title='Инфо', message='Добавление прошло успешно')
            except:
                showinfo(title='Инфо', message='Невозможно добавить,\nмешает связь id \nс другими таблицами или\nдубликат id')
        else:
            showinfo(title='Инфо', message=temp_answ)

    def get_table(self, name):
        # возможно добавить сохранение позиции скроллера если таблица одна и та же
        self.cur_tabn = name
        self.cur_coln = self.col_name[name]
        self.cursor.execute(f'SELECT * FROM {name}\nORDER BY {self.cur_coln[0][0]}')
        cur_table = self.cursor.fetchall()

        self.table_wid.destroy()
        self.scroll.destroy

        self.table_wid = Treeview(self.wind, columns=[i[0] for i in self.cur_coln],
                                  show='headings', selectmode='browse', height=28)
        for i in self.cur_coln:
            self.table_wid.heading(i[0], text=i[0])
            if i[1] == 'integer' or i[1] == 'character':
                self.table_wid.column(i[0], width=80)
        for i in cur_table:
            self.table_wid.insert('', END, values=i)
        self.table_wid.grid(row=0, column=1, rowspan=14, sticky=NSEW)
        self.scroll = Scrollbar(self.wind, orient=VERTICAL, command=self.table_wid.yview)
        self.table_wid.configure(yscroll=self.scroll.set)
        self.scroll.grid(row=0, column=2, rowspan=14, sticky=NS)
        self.table_wid.bind('<<TreeviewSelect>>', self.tab_edit)

    def get_static_info(self):
        self.cursor.execute('''SELECT table_name FROM information_schema.tables
                               WHERE table_schema = 'public'
                               ORDER BY table_name''')
        self.table_name = [i[0] for i in self.cursor.fetchall()]
        for i in self.table_name:
            self.cursor.execute('''SELECT column_name, data_type, character_maximum_length
                                   FROM information_schema.columns
                                   WHERE table_schema = 'public' AND table_name = %s
                                   ORDER BY ordinal_position''', (i,))
            self.col_name[i] = self.cursor.fetchall()