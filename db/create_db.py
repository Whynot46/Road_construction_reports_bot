import aiosqlite
import asyncio


async def create_table():
    async with aiosqlite.connect("./db/database.db") as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                firstname TEXT NOT NULL,
                middlename TEXT,
                lastname TEXT NOT NULL,
                is_active BOOLEAN DEFAULT TRUE
            )
        ''')
        await db.commit()


async def main():
    await create_table()


if __name__ == '__main__':
    asyncio.run(main())