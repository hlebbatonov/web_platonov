import sys

sys.path.append('../')
from app.data.users import Table, User
from app.data import db_session
from sqlalchemy import join


def table_for_user(date):
    db_sess = db_session.create_session()
    date = date.replace('-', '.').strip()
    j = join(User, Table, User.about == Table.group)
    return db_sess.query(Table.time, Table.subject, Table.place).select_from(j).filter(Table.date == date)


def group_in_table(group_name):
    db_sess = db_session.create_session()
    return db_sess.query(Table).filter(Table.group == group_name).first()


def delete_date_from_table(group_name, date):
    db_sess = db_session.create_session()
    return db_sess.query(Table).filter(Table.group == group_name, Table.date == date)
    db_sess.commit()


def insert_into_table(group_name, date, time, subject, place):
    db_sess = db_session.create_session()
    table = Table(group_name=group_name, date=date, time=time, subject=subject, place=place)
    return db_sess.add(table)
    db_sess.commit()


def add(b, curr_date=None, curr_group=None):
    for a in b:
        if a[0] != '' and (a[1] == '' or a[2] != '' or a[3] != ''):
            return 'Неправильно заполнен заголовок файла'
        elif len(a[0]) != 10 or a[0][2] != '.' or a[0][5] != ['.']:
            return 'Неверный формат даты'
        if a[0] != '':
            if group_in_table(a[1]):
                delete_date_from_table(a[1], a[0])
            curr_group = a[1]
            curr_date = a[0]
        elif a[0] == '':
            insert_into_table(curr_group, curr_date, a[1], a[2], a[3])


add([['22.04.2024', '9Б', '', ''], ['', '9:00-10:30', 'Физика', '133'], ['', '15:00-16:30', 'Математика', '109'],
     ['23.04.2024', '10Б', '', ''], ['', '10:00-11:30', 'Алгебра', '111'], ['',
                                                                            '12:30-14:00', 'Геометрия', '110']]
    )
