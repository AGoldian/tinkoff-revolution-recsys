from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton   



class NumbersCallbackFactory(CallbackData, prefix='callback'):
    value: int | None = None
    image_id: int | str | None = None
    group_idt: str | None = None



def get_inline_keybord(image_id: int, group_idt: str):
    builder = InlineKeyboardBuilder()
    builder.button(
        text="😠", callback_data=NumbersCallbackFactory(value=0, image_id=image_id, group_idt=group_idt)
    )
    builder.button(
        text="👍", callback_data=NumbersCallbackFactory(value=1, image_id=image_id, group_idt=group_idt)
    )
    builder.button(
        text="🔥", callback_data=NumbersCallbackFactory(value=2, image_id=image_id, group_idt=group_idt)
    )
    builder.adjust(3)
    return builder.as_markup()


class UserStates(StatesGroup):
    choosing_categories = State()  # Состояние для выбора категорий


categories_keyboard = InlineKeyboardMarkup(row_width=2, inline_keyboard=[
    [
        InlineKeyboardButton(text="Одежда и акссесуары", callback_data="category_Одежда и акссесуары"),
        InlineKeyboardButton(text="Образование", callback_data="category_Образование"),
    ],
    [
        InlineKeyboardButton(text="Здоровье", callback_data="category_Здоровье"),
        InlineKeyboardButton(text="Еда и сервисы", callback_data="category_Еда и сервисы"),
    ],
    [
        InlineKeyboardButton(text="Дом и маркетплейсы", callback_data="category_Дом и маркетплейсы"),
        InlineKeyboardButton(text="Поездки и путешествия", callback_data="category_Поездки и путешествия")
    ],
    [
        InlineKeyboardButton(text="Подтвердить выбор", callback_data="confirm_selection")
    ]
])
