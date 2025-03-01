import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from bot.handlers import router
from bot.config import Config
from bot.database.db import init_db


async def main():
    bot = Bot(token=Config.TELEGRAM_TOKEN)
    dp = Dispatcher(bot=bot, storage=MemoryStorage())
    dp.include_router(router)
    await init_db()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

                
if __name__ == "__main__":
    try:
        print('Bot is running...')
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')