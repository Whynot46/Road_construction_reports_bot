import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from bot.handlers import router, send_morning_notification, send_evening_notification
from bot.config import Config
from bot.database.db import init_db
from bot.services.google_api_service import update_users, update_projects


async def main():
    try:
        bot = Bot(token=Config.TELEGRAM_TOKEN)
        dp = Dispatcher(bot=bot, storage=MemoryStorage())

        scheduler = AsyncIOScheduler()
        scheduler.add_job(
            func=send_morning_notification,
            trigger=CronTrigger(hour=8, minute=00, timezone="Europe/Moscow"),  # 08:00 МСК
            args=(bot,),
            id="morning_notification"
        )
        scheduler.add_job(
            func=send_evening_notification,
            trigger=CronTrigger(hour=20, minute=0, timezone="Europe/Moscow"),  # 20:00 МСК
            args=(bot,),
            id="evening_notification"
        )
        scheduler.add_job(
            func=update_users,
            trigger=CronTrigger(hour="*", minute=0, timezone="Europe/Moscow"),  # Каждый час в 0 минут
            id="update_users"
        )
        scheduler.add_job(
            func=update_projects,
            trigger=CronTrigger(hour="*", minute=0, timezone="Europe/Moscow"),  # Каждый час в 0 минут
            id="update_projects"
        )
        # scheduler.add_job(
        #     func=update_reports,
        #     trigger=CronTrigger(minute="*/1", timezone="Europe/Moscow"),  # Каждые 10 минут
        #     id="upload_not_uploaded_reports"
        # )
        scheduler.start() 
        
        dp.include_router(router)
        await init_db()
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

    except Exception as e:
        print(f"Bot error: {e}")

    finally:
        await bot.session.close()
        await dp.stop_polling()
        await bot.delete_webhook(drop_pending_updates=True)
        await scheduler.shutdown()


                
if __name__ == "__main__":
    try:
        print('Bot is running...')
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
