import asyncio
import logging
import aiofiles

import os
import csv

from config_reader import config

from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command, CommandStart
from aiogram.fsm.context import FSMContext
from keybords.inline_keybords import categories_keyboard, UserStates

from handlers.basic import start_bot
from keybords.inline_keybords import get_inline_keybord, NumbersCallbackFactory

from models.agi import AGIModel
from models.agi import translate_agg_to_group, all_group

logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.bot_token.get_secret_value())
dp = Dispatcher()
file_ids = set()


# Создайте словарь для хранения доступных изображений для каждого пользователя
user_model_memory = {}
user_start_category = {}

# Функция для случайного выбора изображения для пользователя
def get_agi_image(user_id):
    print(user_id)
    personal_model: AGIModel = user_model_memory[user_id]
    file_name, group = personal_model.next_element()

    if file_name is None:
        return None, None

    file_path = '/'.join([group, file_name])

    return file_path, group

async def send_random_image(message: types.Message, user_id, state: FSMContext):
    print('SEND RANDOM', str(user_id))
    user_data = await state.get_data()
    if user_data.get('processing', False):
        return  # Пропускаем, если другой процесс обработки уже запущен
    user_data['processing'] = True  # Устанавливаем флаг обработки

    try:
        random_image, group = get_agi_image(user_id)
        file_ids = []
        if random_image:
            with open(os.path.join('offers', random_image), 'rb') as image_from_buffer:
                result = await message.answer_photo(types.BufferedInputFile(
                    image_from_buffer.read(),
                    filename=random_image
                    ),
                    caption=' '.join(['Сategory:', group]),
                    reply_markup=get_inline_keybord(image_id=random_image, group_idt=group)
                )       
            file_ids.append(result.photo[-1].file_id)

        else:
            await message.answer("No more images available for you.")
    finally:

        user_data['processing'] = False

active_users_rec = set()


@dp.message(Command('rec'))
async def cmd_start(message: types.Message, state: FSMContext, user_id=None):
    if user_id is None:
        user_id = message.from_user.id
    print('REC', str(user_id))
    if user_id in active_users_rec:
        await message.answer("Процесс выбора уже запущен. Пожалуйста, подождите.")
        return
    active_users_rec.add(user_id)

    try:
        await send_random_image(message, user_id, state=state)
    finally:
        active_users_rec.remove(user_id)


active_users = set()

@dp.callback_query(NumbersCallbackFactory.filter())
async def callbacks_num_change_fab(callback: types.CallbackQuery,
                                   callback_data: NumbersCallbackFactory,
                                   state: FSMContext):
    print('CALLBACK', str(callback.from_user.id))

    await bot.edit_message_reply_markup(
                chat_id=callback.from_user.id,
                message_id=callback.message.message_id,
                reply_markup=None
            )
    user_id = callback.from_user.id
    item_id = callback_data.image_id
    reaction = callback_data.value
    if user_id in active_users:
        return  # Пропускаем, если пользователь уже активен
    active_users.add(user_id)

    try:
        await cmd_start(callback.message, state, user_id)
        await callback.answer()
        print('UPDATE', str(user_id))
        user_model_memory[user_id].update(callback_data.group_idt, callback_data.value)

        if callback_data.value < 1:
            await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)

        else:
            await bot.edit_message_caption(
                chat_id=callback.from_user.id,
                message_id=callback.message.message_id,
                caption='😍'
            )

    finally:
        active_users.remove(user_id)  # Снимаем флаг обработк
        # Register the user's action in a CSV file with UTF-8 encoding
        async with aiofiles.open("user_actions.csv", "a", newline="", encoding="utf-8") as csvfile:
            fieldnames = ["user_id", "item_id", "reaction"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            await writer.writerow({"user_id": user_id, "item_id": item_id, "reaction": reaction})


@dp.message(Command('start'))
async def start(message: types.Message, state):
    await state.set_state(UserStates.choosing_categories)
    await message.answer("Выберите интересующие вас категории:", reply_markup=categories_keyboard)


@dp.callback_query(lambda callback_query: callback_query.data.startswith("category_"))
async def process_category_selection(callback_query: types.CallbackQuery, state: FSMContext):
    category = callback_query.data.split('_')[1]
    user_data = await state.get_data()
    selected_categories = user_data.get('selected_categories', [])

    if category in selected_categories:
        # Если категория уже выбрана, уберите ее из списка
        selected_categories.remove(category)
    else:
        # Иначе добавьте категорию в список
        selected_categories.append(category)

    # Обновите текст сообщения, чтобы отразить выбранные категории
    updated_message = f"Выбранные категории: {', '.join(selected_categories)}"

    await bot.edit_message_text(
        updated_message,
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        reply_markup=categories_keyboard
    )

    # Сохраните обновленные данные в состоянии FSM
    await state.update_data(selected_categories=selected_categories)


@dp.callback_query(lambda callback_query: callback_query.data == "confirm_selection")
async def confirm_selection(callback_query: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    selected_categories = user_data.get('selected_categories', [])

    if not selected_categories:
        await bot.send_message(
            callback_query.from_user.id,
            "Вы не выбрали ни одной категории. Выберите хотя бы одну категорию перед подтверждением."
        )
    else:
        user_id = callback_query.from_user.id
        user_start_category[user_id] = selected_categories
        
        all_input_category = all_group
        select_input_category = []
        [select_input_category.extend(translate_agg_to_group[name]) for name in selected_categories]
        user_model_memory[user_id] = AGIModel(all_input_category, select_input_category)
        print(user_model_memory)

        await bot.send_message(
            callback_query.from_user.id,
            f"Выбранные категории сохранены. {selected_categories}  Вы можете начать покупки в выбранных категориях."
        )
        await cmd_start(callback_query.message, state, user_id)

    await state.clear()


async def main():
    dp.startup.register(start_bot)

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
