import sqlite3


def class_in_table(class_name):
    con = sqlite3.connect('data/timetable.db', check_same_thread=False)
    cur = con.cursor()
    return (cur.execute("""SELECT class
      FROM timetable
     WHERE class= ?
    """, (class_name,)))
    # con.commit()


def delete_date_from_table(class_name, date):
    con = sqlite3.connect('data/timetable.db', check_same_thread=False)
    cur = con.cursor()
    cur.execute("""DELETE FROM timetable
          WHERE class = ? AND 
                date = ?
    """, (class_name, date))
    con.commit()


def insert_into_table(class_name, date, time, subject, place):
    con = sqlite3.connect('data/timetable.db', check_same_thread=False)
    cur = con.cursor()
    cur.execute("""INSERT INTO timetable (
                              id,
                              class,
                              date,
                              time,
                              subject,
                              place
                          )
                          VALUES (
                              NULL,
                              ?,
                              ?,
                              ?,
                              ?,
                              ?
                          );
                """, (class_name, date, time, subject, place))
    con.commit()


def add(b, curr_class=None, curr_date=None):
    for a in b:
        if a[0] != '' and (a[1] == '' or a[2] != '' or a[3] != ''):
            return 'Неправильно заполнен заголовок файла'
        elif len(a[0]) != 10 or a[0][2] != '.' or a[0][5] != ['.']:
            return 'Неверный формат даты'
        if a[0] != '':
            if class_in_table(a[1]).fetchone():
                delete_date_from_table(a[1], a[0])
            curr_class = a[1]
            curr_date = a[0]
        elif a[0] == '':
            insert_into_table(curr_class, curr_date, a[1], a[2], a[3])
