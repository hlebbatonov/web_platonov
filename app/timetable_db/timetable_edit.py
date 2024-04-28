import sys

sys.path.append('../')
from app.data.users import Table, User
from app.data import db_session
from sqlalchemy import join


def select_all_timetable():
    db_session.global_init("data/users.db")
    db_sess = db_session.create_session()
    return db_sess.query(Table).all()


def table_for_user(date, curr_user_group):
    db_session.global_init("data/users.db")
    db_sess = db_session.create_session()
    date = date.replace('-', '.').strip()
    return db_sess.query(Table.time, Table.subject, Table.place).filter(Table.date == date,
                                                                        Table.group == curr_user_group).all()


def group_in_table(group_name):
    db_session.global_init("data/users.db")
    db_sess = db_session.create_session()
    return db_sess.query(Table).filter(Table.group == group_name).first()


def delete_date_from_table(group_name, date):
    db_session.global_init("data/users.db")
    db_sess = db_session.create_session()
    db_sess.query(Table).filter(Table.group == group_name, Table.date == date).delete()
    db_sess.commit()


def insert_into_table(group_name, date, time, subject, place):
    db_session.global_init("data/users.db")
    db_sess = db_session.create_session()
    table = Table(group=group_name, date=date, time=time, subject=subject, place=place)
    db_sess.add(table)
    db_sess.commit()


def add(b, curr_date=None, curr_group=None):
    for a in b:
        if a[0] != '' and (a[1] == '' or a[2] != '' or a[3] != ''):
            return 'Неправильно заполнен заголовок файла'
        elif a[0] != '' and (len(a[0]) != 10 or a[0][2] != '.' or a[0][5] != '.'):
            return 'Неверный формат даты'
        if a[0] != '':
            if group_in_table(a[1]):
                delete_date_from_table(a[1], a[0])
            curr_group = a[1]
            curr_date = a[0]
        elif a[0] == '':
            insert_into_table(curr_group, curr_date, a[1], a[2], a[3])
