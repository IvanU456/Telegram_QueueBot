import configparser
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import client_kb as nav
import db_functions as db


config = configparser.ConfigParser()
config.read('config.ini')
token = config['queueBot']['api']


bot = Bot(token=token)
dp = Dispatcher(bot)


async def on_startup(_):
    db.start_up()


@dp.message_handler(commands=['start'])
async def command_start(message: types.Message):
    info = db.user_check(message.from_user.id)
    if info is None:
        await bot.send_message(message.from_user.id, 'Вас нет в базе используйте команду "/add Фамилия Имя номер группы"')
    else:
        await bot.send_message(message.from_user.id, 'menu', reply_markup=nav.mainMenu)
        await message.delete()


@dp.message_handler(commands=['add'])
async def command_add(message: types.Message):
    user = message.text.replace('/add ', '').split(' ')
    db.add_user(user, message.from_user.id)
    await bot.send_message(message.from_user.id, 'Вы успешно добавлены в базу', reply_markup=nav.mainMenu)


@dp.message_handler(commands=['Встать_в_очередь'])
async def create_queue(message: types.Message):
    await bot.send_message(message.from_user.id, 'Выберите преподавателя', reply_markup=nav.teachersList)
    await message.delete()


@dp.message_handler(commands=[x[0].replace('/', '') for x in nav.teachersList['keyboard']])
async def teachers(message: types.Message):
    global teacher
    await bot.send_message(message.from_user.id, 'Выберите день недели', reply_markup=nav.weekDays)
    teacher = message.text.replace("/", "")


@dp.message_handler(commands=['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота'])
async def week_days(message: types.Message):
    global day
    await bot.send_message(message.from_user.id, 'Выберите время', reply_markup=nav.timeList)
    day = message.text.replace("/", "")


@dp.message_handler(commands=[x[0].replace('/', '') for x in nav.timeList['keyboard']])
async def time_btn(message: types.Message):
    table = f'{teacher}_{day}_{message.text.replace("/", "").replace(":", "_")}'
    await bot.send_message(message.from_user.id, f'Вы встали в очередь к преподавателю {teacher}. Дата: {day} '
                                                 f'{message.text.replace("/", "")}', reply_markup=nav.mainMenu)
    db.create_queue(table, message.from_user.id)


@dp.message_handler(commands=['Доступные_очереди'])
async def get_queues(message: types.Message):
    queues = db.get_queues()
    if len(queues) > 0:
        for queue in queues:
            await bot.send_message(message.from_user.id, queue[1], reply_markup=InlineKeyboardMarkup(row_width=3).add(
                InlineKeyboardButton(text='Войти', callback_data=f'join {queue[0]}'),
                InlineKeyboardButton(text='Выйти', callback_data=f'leave {queue[0]}'),
                InlineKeyboardButton(text='Приоритет', callback_data=f'priority {queue[0]}')
            ))
    else:
        await bot.send_message(message.from_user.id, 'Пока нет очередей')


@dp.message_handler(commands=['Мои_очереди'])
async def my_queues(message: types.Message):
    queues = db.my_queues(message.from_user.id)
    if queues is not None:
        for queue in queues:
            await bot.send_message(message.from_user.id, queue[1], reply_markup=InlineKeyboardMarkup(row_width=2).add(
                InlineKeyboardButton(text='Доздача', callback_data=f'go_first {queue[0]}'),
                InlineKeyboardButton(text='Выйти', callback_data=f'leave {queue[0]}')
            ))
    else:
        await bot.send_message(message.from_user.id, 'У вас пока нет очередей')


@dp.callback_query_handler(lambda x: x.data and x.data.startswith('leave '))
async def leave_callback(callback_query: types.CallbackQuery):
    await callback_query.answer(text=f'Вы покинули очередь {callback_query.data.replace("leave ", "")}', show_alert=True)
    db.leave_queue(callback_query.from_user.id, callback_query.data.replace("leave ", ""))


@dp.callback_query_handler(lambda x: x.data and x.data.startswith('join '))
async def join_callback(callback_query: types.CallbackQuery):
    await callback_query.answer(text=f'Вы присоединились к очереди {callback_query.data.replace("join ", "")}', show_alert=True)
    db.join_queue(callback_query.from_user.id, callback_query.data.replace("join ", ""))


@dp.callback_query_handler(lambda x: x.data and x.data.startswith('go_first '))
async def go_first(callback_query: types.CallbackQuery):
    await callback_query.answer(text=f'Вы записались на доздачу в очередь {callback_query.data.replace("go_first ", "")}', show_alert=True)
    db.go_first(callback_query.from_user.id, callback_query.data.replace("go_first ", ""))


@dp.callback_query_handler(lambda x: x.data and x.data.startswith('priority '))
async def priority_join(callback_query: types.CallbackQuery):
    await callback_query.answer(text=f'Вы записались в приорететную очередь {callback_query.data.replace("priority ", "")}', show_alert=True )
    db.join_queue(callback_query.from_user.id, f'{callback_query.data.replace("priority ", "")}_p')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
