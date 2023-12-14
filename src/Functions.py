from datetime import datetime


def window_to_center(window):
    x = (window.winfo_screenwidth() - window.winfo_reqwidth()) / 2 - 300
    y = (window.winfo_screenheight() - window.winfo_reqheight()) / 2 - 200
    window.geometry("+%d+%d" % (x, y))


def check_text(s):
    if s is None:
        return False
    if len(s) == 0 or len(s) > 60:
        return False
    for c in s:
        if not c.isalpha() and c not in ' \'':
            return False
    return True


def check_date(input_date):
    try:
        temp_date = datetime.strptime(input_date, '%Y-%m-%d')
        temp_to_old = datetime.strptime('1900-1-1', '%Y-%m-%d')
        if temp_date < temp_to_old or temp_date > datetime.now():
            return False
        return True
    except:
        return False
