from aiogram import Bot
from config_reader import config


admin_id = config.admin_token.get_secret_value()

async def start_bot(bot: Bot):
    await bot.send_message(int(admin_id), text='Bot started')