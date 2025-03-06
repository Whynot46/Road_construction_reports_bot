import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from bot.handlers import router, send_morning_notification, send_evening_notification
from bot.config import Config
from bot.database.db import init_db
from bot.services.google_api_service import update_users, update_projects, upload_not_uploaded_reports


async def main():
    bot = Bot(token=Config.TELEGRAM_TOKEN)
    dp = Dispatcher(bot=bot, storage=MemoryStorage())
    scheduler = AsyncIOScheduler()

    try:
        await init_db()

        scheduler.add_job(
            func=send_morning_notification,
            trigger=CronTrigger(hour=8, minute=0, timezone="Europe/Moscow"),  # 08:00 МСК
            args=(bot,),  # Pass the bot instance
            id="morning_notification"
        )
        scheduler.add_job(
            func=send_evening_notification,
            trigger=CronTrigger(hour=20, minute=0, timezone="Europe/Moscow"),  # 20:00 МСК
            args=(bot,),  # Pass the bot instance
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
        scheduler.add_job(
            func=upload_not_uploaded_reports,
            trigger=CronTrigger(hour="*", minute=0, timezone="Europe/Moscow"),  # Каждый час в 0 минут
            id="upload_not_uploaded_reports"
        )


        scheduler.start()
        dp.include_router(router)

        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

    except Exception as error:
        print(f"Bot error: {error}")

    finally:
        await bot.session.close()
        if scheduler.running:
            await scheduler.shutdown()
        if hasattr(dp, '_polling') and dp._polling:
            await dp.stop_polling()

if __name__ == "__main__":
    try:
        print('Bot is running...')
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')