from aiogram.filters.state import StatesGroup, State


class Test(StatesGroup):
    """Объекты класса State - состояния, передаваемые как параметры для декоратора функции.
     Определяют хэндлер, в который пойдет следующее сообщения от пользователя.
     """
    Q1 = State()
    Q2 = State()
    Q2_1 = State()
    Q3 = State()
    Q3_1 = State()
