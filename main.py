import logging
# from os import getenv
# from sys import exit
from aiogram import Bot, types, Dispatcher
#from aiogram.dispatcher import FSMContext
from states import Test
from aiogram.fsm.storage.memory import MemoryStorage
from database import SQL
from datetime import date
from test import Test_for_function as Ts
import aiogram.utils.markdown as fmt

# bot_token = getenv('BOT_TOKEN')
# if not bot_token:
#     exit('Error: no token provided')

bot_token = '5406778011:AAFzN1qRr30v9Xqvv3vh1ImjfDjk6F7vBmk'

bot = Bot(token=bot_token)
dp = Dispatcher(storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)
db_path = 'database.db'
raw_date = date.today()
today = '{}.{}.{}'.format(raw_date.day, raw_date.month, raw_date.year)
buttons = ['Сделать запись', 'Показать записи', 'Удалить записи']
main_keyboard = types.ReplyKeyboardMarkup()
main_keyboard.add(*buttons)


@dp.message_handler(commands='start')
async def start_func(message: types.Message):
    """Точка входа для начала работы с ботом."""

    await message.answer(text='Привет, выбери действие снизу:', reply_markup=main_keyboard)


@dp.message_handler(commands='help')
async def help_func(message: types.Message):
    """Показывает важную информацию."""

    await message.answer(text='Пример записи даты:  7.3.2019\n\nЕсли у вас есть какие-либо '
                              'пожелания или идеи по улучшению бота - пишите https://t.me/michaylo34')


@dp.message_handler()
async def buttons_handler(message: types.Message):
    """Обрабатывает текстовые значения кнопок основной клавиатуры."""

    if message.text == 'Сделать запись':
        await message.answer(text='Внимание, написанную заметку изменить будет нельзя! Назад  -  /back')
        await Test.Q1.set()
    elif message.text == 'Показать записи':
        keyboard_for_showing = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        buttons_for_showing = ['Показать записи по дате', 'Показать все записи']
        keyboard_for_showing.add(*buttons_for_showing)
        await message.answer(text='Выберите способ показа. Назад  -  /back', reply_markup=keyboard_for_showing)
        await Test.Q2.set()
    elif message.text == 'Удалить записи':
        keyboard_for_remove = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        buttons_for_remove = ['Удалить все записи по дате', 'Очистить историю записей']
        keyboard_for_remove.add(*buttons_for_remove)
        await message.answer(text='Выберите способ удаления. Назад  -  /back', reply_markup=keyboard_for_remove)
        await Test.Q3.set()
    else:
        await message.answer(text='Выберите действие из списка:', reply_markup=main_keyboard)


@dp.message_handler(state=Test.Q1)
async def write_note_func(message: types.Message, state: FSMContext):
    """Логика добавления новой записи."""

    user_id = message.from_user.id
    user_answer = message.text
    await state.update_data(note_text=user_answer)
    data = await state.get_data()
    note_text = data.get('note_text')
    if note_text == '/back':
        await state.reset_state(with_data=True)
        await message.answer(text='Выберите действие из списка:', reply_markup=main_keyboard)
    else:
        await state.reset_state(with_data=False)
        db = SQL(db_path)
        data_list = (user_id, today, note_text)
        db.write_note(data=data_list)
        db.close_connection()
        await message.answer('Заметка создана!', reply_markup=main_keyboard)


@dp.message_handler(state=Test.Q2)
async def show_notes_func(message: types.Message, state: FSMContext):
    """Обрабатывает кнопки клавиатуры для показа записей, логика показа всех записей."""

    user_id = message.from_user.id
    user_answer = message.text
    await state.update_data(value_for_showing=user_answer)
    data = await state.get_data()
    value_for_showing = data.get('value_for_showing')
    if value_for_showing == '/back':
        await state.reset_state(with_data=True)
        await message.answer(text='Выберите действие из списка:', reply_markup=main_keyboard)
    else:
        await state.reset_state(with_data=False)
        if value_for_showing == 'Показать записи по дате':
            await message.answer(text='Введите дату. Назад  -  /back')
            await Test.Q2_1.set()
        elif value_for_showing == 'Показать все записи':
            db = SQL(db_path)
            data_list = db.show_all_notes(user_id)
            db.close_connection()

            test_variable = Ts()
            if test_variable.test_data_list(data_list) is True:
                for data in data_list:
                    note_text = data[0]
                    note_date = data[1]
                    await message.answer(text='{}\n{}'.format(note_text, fmt.text(fmt.hbold(note_date))),
                                         reply_markup=main_keyboard)
            else:
                await message.answer(text='Похоже, у вас нет ни одной записи :(', reply_markup=main_keyboard)
        else:
            await message.answer(text='Выберите действие из списка:', reply_markup=main_keyboard)


@dp.message_handler(state=Test.Q2_1)
async def show_notes_by_date_func(message: types.Message, state: FSMContext):
    """Логика показа записей по дате."""

    user_id = message.from_user.id
    user_answer = message.text
    await state.update_data(date_for_showing=user_answer)
    data = await state.get_data()
    date_for_showing = data.get('date_for_showing')
    if date_for_showing == '/back':
        await state.reset_state(with_data=True)
        await message.answer(text='Выберите действие из списка:', reply_markup=main_keyboard)
    else:
        await state.reset_state(with_data=False)
        db = SQL(db_path)
        data_list = db.show_notes_by_date(date_for_showing, user_id)
        db.close_connection()

        test_variable = Ts()
        if test_variable.test_data_list(data_list) is True:
            for data in data_list:
                note_text = data[0]
                await message.answer(text='{}\n{}'.format(note_text, fmt.text(fmt.hbold(date_for_showing))),
                                     reply_markup=main_keyboard)
        else:
            await message.answer(text='Похоже, у вас нет ни одной записи с такой датой :(', reply_markup=main_keyboard)


@dp.message_handler(state=Test.Q3)
async def remove_notes_func(message: types.Message, state: FSMContext):
    """Обрабатывает кнопки для удаления сообщений, логика удаления всех сообщений."""

    user_id = message.from_user.id
    user_answer = message.text
    await state.update_data(value_for_removing=user_answer)
    data = await state.get_data()
    value_for_removing = data.get('value_for_removing')
    if value_for_removing == '/back':
        await state.reset_state(with_data=True)
        await message.answer(text='Выберите действие из списка:', reply_markup=main_keyboard)
    else:
        await state.reset_state(with_data=False)
        if value_for_removing == 'Удалить все записи по дате':
            await message.answer(text='Введите дату. Назад  -  /back')
            await Test.Q3_1.set()
        elif value_for_removing == 'Очистить историю записей':
            db = SQL(db_path)
            db.remove_all_notes(user_id)
            db.close_connection()
            await message.answer(text='Все записи успешно удалены :)', reply_markup=main_keyboard)
        else:
            await message.answer(text='Выберите действие из списка:', reply_markup=main_keyboard)


@dp.message_handler(state=Test.Q3_1)
async def remove_by_date_func(message: types.Message, state: FSMContext):
    """Логика удаления записей по дате."""

    user_id = message.from_user.id
    user_answer = message.text
    await state.update_data(date_for_remove=user_answer)
    data = await state.get_data()
    date_for_remove = data.get('date_for_remove')
    if date_for_remove == '/back':
        await state.reset_state(with_data=True)
        await message.answer(text='Выберите действие из списка:', reply_markup=main_keyboard)
    else:
        await state.reset_state(with_data=False)
        db = SQL(db_path)
        test_list = db.show_notes_by_date(date_for_remove, user_id)
        if test_list:
            db.remove_notes_by_date(date_for_remove, user_id)
            db.close_connection()
            await message.answer(text='Записи успешно удалены :)', reply_markup=main_keyboard)
        else:
            await message.answer(text='Возможно записей с такой датой нет, или вы ошиблись в написании',
                                 reply_markup=main_keyboard)


if __name__ == '__main__':
    Dispatcher.start_polling(dp, skip_updates=True)
