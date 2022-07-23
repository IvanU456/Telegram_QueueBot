import sqlite3


def start_up():
    global db, cursor
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    db.execute(""" CREATE TABLE IF NOT EXISTS students(id INT, surname TEXT, name TEXT, groups INT) """)
    db.commit()


def user_check(user_id):
    info = cursor.execute(f""" SELECT surname, name, groups FROM students WHERE id ={user_id} """)
    db.commit()
    return info.fetchone()


def add_user(user, user_id):
    cursor.execute(f""" INSERT INTO students (id ,surname, name, groups) 
            VALUES('{user_id}', '{user[0].replace(',','')}', '{user[1].replace(',','')}', {user[2]}) """)
    db.commit()


def create_queue(table, user_id):
    try:
        cursor.execute(f""" CREATE TABLE {table} (id INT, surname TEXT, name TEXT, groups INT) """)
        cursor.execute(f""" CREATE TABLE {table}_p (id INT, surname TEXT, name TEXT, groups INT) """)
        cursor.execute(f""" INSERT INTO {table} (id, surname, name, groups) 
                                    SELECT id, surname, name, groups FROM students 
                                    WHERE id = {user_id} """)
        db.commit()
    except sqlite3.OperationalError as ex:
        cursor.execute(f""" INSERT INTO {table} (id, surname, name, groups) 
                                    SELECT id, surname, name, groups FROM students 
                                    WHERE id = {user_id} """)
        db.commit()


def get_queues():
    all_queues = []
    cursor.execute(""" SELECT name from sqlite_master where type= 'table' """)
    for table in cursor.fetchall()[2:]:
        if table[0].split('_')[-1] != 'p':
            i = 0
            queue = f'Очердь: {table[0]}'
            cursor.execute(f""" SELECT surname, name, groups FROM {table[0]}_p""")
            for member in cursor.fetchall():
                i += 1
                queue += f'\n{" "*10}{i}) {member[0]} {member[1]} {member[2]}'
            cursor.execute(f""" SELECT surname, name, groups FROM {table[0]}""")
            for member in cursor.fetchall():
                i += 1
                queue += f'\n{" " * 10}{i}) {member[0]} {member[1]} {member[2]}'
            all_queues.append((table[0], queue))
        db.commit()
    return all_queues


def my_queues(user_id):
    all_queues = []
    cursor.execute(""" SELECT name from sqlite_master where type= 'table' """)
    for table in cursor.fetchall()[2:]:
        i = 0
        cursor.execute(f""" SELECT surname, name, groups FROM {table[0]} WHERE id = {user_id}""")
        if len(cursor.fetchall()) > 0:
            queue = f'Очердь: {table[0].replace("_p", "")}'
            cursor.execute(f""" SELECT surname, name, groups FROM {table[0].replace("_p", "")}_p""")
            for member in cursor.fetchall():
                i += 1
                queue += f'\n{" " * 10}{i}) {member[0]} {member[1]} {member[2]}'
            cursor.execute(f""" SELECT surname, name, groups FROM {table[0].replace("_p", "")}""")
            for member in cursor.fetchall():
                i += 1
                queue += f'\n{" " * 10}{i}) {member[0]} {member[1]} {member[2]}'
            all_queues.append((table[0], queue))
        db.commit()
    for i in range(len(all_queues)):
        try:
            if all_queues[i][0] == all_queues[i + 1][0].replace('_p', ''):
                all_queues.pop(i + 1)
        except IndexError:
            return all_queues


def leave_queue(user_id, table):
    cursor.execute(f""" DELETE FROM {table} WHERE id = {user_id}""")
    cursor.execute(f""" Select * FROM {table.replace('_p', '')} """)
    if cursor.fetchone() is None:
        cursor.execute(f""" DROP TABLE {table.replace('_p', '')} """)
        cursor.execute(f""" DROP TABLE {table.replace('_p', '')}_p """)
    db.commit()


def join_queue(user_id, table):
    cursor.execute(f""" INSERT INTO {table} (id, surname, name, groups) 
                                    SELECT id, surname, name, groups FROM students 
                                    WHERE id = {user_id} """)
    db.commit()


def go_first(user_id, table):
    cursor.execute(f""" SELECT * FROM {table}_p""")
    queue = (cursor.fetchall()[::-1])
    me = cursor.execute(f""" SELECT * FROM students WHERE id = {user_id} """).fetchone()
    queue.append(me)
    cursor.execute(f""" DELETE FROM {table}_p """)
    cursor.executemany(f""" INSERT INTO {table}_p (id, surname, name, groups) VALUES (?,?,?,?) """, queue[::-1])
