from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import sqlite3

i = 6

btnQueue = KeyboardButton('/Встать_в_очередь')
btnAllQueues = KeyboardButton('/Доступные_очереди')
btnMyQueues = KeyboardButton('/Мои_очереди')
mainMenu = ReplyKeyboardMarkup(resize_keyboard=True).add(btnQueue, btnAllQueues, btnMyQueues)


teachersList = ReplyKeyboardMarkup(row_width=2)
with sqlite3.connect('database.db') as db:
    cursor = db.cursor()
    cursor.execute(""" SELECT * FROM teachers""")
    for teacher in cursor:
        teachersList.row(f'/{teacher[0]}_{teacher[1]}_{teacher[2]}')


weekDays = ReplyKeyboardMarkup(row_width=2).add(
    KeyboardButton('/Понедельник'),
    KeyboardButton('/Вторник'),
    KeyboardButton('/Среда'),
    KeyboardButton('/Четверг'),
    KeyboardButton('/Пятница'),
    KeyboardButton('/Суббота')
)


timeList = ReplyKeyboardMarkup(row_width=2)
while i < 18:
    i += 2
    timeList.row(f'/{i}:00')
