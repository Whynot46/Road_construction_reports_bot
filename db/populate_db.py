import aiosqlite
import asyncio


DB_PATH = "./db/database.db"

async def populate_database():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            INSERT INTO users (user_id, firstname, middlename, lastname, is_active)
            VALUES (?, ?, ?, ?, ?)
        ''', (7348838870, "Алексей", "Дмитриевич", "Пахалев", True))
        await db.execute('''
            INSERT INTO construction_projects (name, is_active)
            VALUES (?, ?)
        ''', ("Объект 1", True))

        await db.execute('''
            INSERT INTO construction_projects (name, is_active)
            VALUES (?, ?)
        ''', ("Объект 2", True))

        await db.execute('''
            INSERT INTO construction_projects (name, is_active)
            VALUES (?, ?)
        ''', ("Объект 3", True))

        await db.commit()


if __name__ == '__main__':
    asyncio.run(populate_database())