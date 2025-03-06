import aiosqlite
import asyncio


DB_PATH = "./db/database.db"


async def clear_database():
    async with aiosqlite.connect(DB_PATH) as db:
        tables = [
            "users",
            "admins",
            "construction_projects",
            "preparatory_reports",
            "earthworks_reports",
            "artificial_structures_reports",
            "road_clothing_reports",
            "asphalt_clothing_reports",
        ]

        for table in tables:
            await db.execute(f"DELETE FROM {table};")

        await db.commit()


if __name__ == '__main__':
    asyncio.run(clear_database())