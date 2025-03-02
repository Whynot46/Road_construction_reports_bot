import aiosqlite
import asyncio


DB_PATH = "./db/database.db"


async def create_table():
    async with aiosqlite.connect(DB_PATH) as db:
        # Создание таблицы users
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

        # Создание таблицы preparatory_reports
        await db.execute('''
            CREATE TABLE IF NOT EXISTS preparatory_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                create_datetime TEXT NOT NULL,
                is_uploaded_to_cloud BOOLEAN DEFAULT FALSE,
                upload_datetime TEXT,
                route_breakdown FLOAT,
                clearing_way FLOAT,
                water_disposal TEXT,
                water_disposal_scope TEXT,
                removal_utility_networks TEXT,
                removal_utility_networks_scope TEXT,
                temporary_construction FLOAT,
                quarries_construction TEXT,
                quarries_construction_quantity FLOAT,
                cutting_asphalt_area FLOAT,
                other_works TEXT,
                photo_links TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')

        # Создание таблицы earthworks_reports
        await db.execute('''
            CREATE TABLE IF NOT EXISTS earthworks_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                create_datetime TEXT NOT NULL,
                is_uploaded_to_cloud BOOLEAN DEFAULT FALSE,
                upload_datetime TEXT,
                detailed_breakdown TEXT,
                excavations_development TEXT,
                excavations_development_quantity FLOAT,
                soil_compaction TEXT,
                soil_compaction_quantity TEXT,
                final_layout TEXT,
                final_layout_quantity FLOAT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')

        # Создание таблицы artificial_structures_reports
        await db.execute('''
            CREATE TABLE IF NOT EXISTS artificial_structures_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                create_datetime TEXT NOT NULL,
                is_uploaded_to_cloud BOOLEAN DEFAULT FALSE,
                upload_datetime TEXT,
                work_type TEXT,
                work_scope TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')

        # Создание таблицы road_clothing_reports
        await db.execute('''
            CREATE TABLE IF NOT EXISTS road_clothing_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                create_datetime TEXT NOT NULL,
                is_uploaded_to_cloud BOOLEAN DEFAULT FALSE,
                upload_datetime TEXT,
                underlying_layer TEXT,
                underlying_layer_area TEXT,
                additional_layer TEXT,
                additional_layer_area TEXT,
                foundation_construction TEXT,
                foundation_construction_area TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')

        # Создание таблицы asphalt_clothing_reports
        await db.execute('''
            CREATE TABLE IF NOT EXISTS asphalt_clothing_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                create_datetime TEXT NOT NULL,
                is_uploaded_to_cloud BOOLEAN DEFAULT FALSE,
                upload_datetime TEXT,
                cleaning_base TEXT,
                cleaning_base_area FLOAT,
                installation_primer TEXT,
                installation_primer_area FLOAT,
                asphalt_mixture_lower TEXT,
                asphalt_mixture_lower_area TEXT,
                asphalt_mixture_upper TEXT,
                asphalt_mixture_upper_area TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')

        # Создание таблицы material_consumption_reports
        await db.execute('''
            CREATE TABLE IF NOT EXISTS material_consumption_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                create_datetime TEXT NOT NULL,
                is_uploaded_to_cloud BOOLEAN DEFAULT FALSE,
                upload_datetime TEXT,
                stage TEXT,
                pgs_quantity FLOAT,
                crushed_stone_fraction TEXT,
                crushed_stone_quantity FLOAT,
                side_stone TEXT,
                side_stone_quantity FLOAT,
                ebdc_quantity FLOAT,
                asphalt_concrete_mixture TEXT,
                asphalt_concrete_scope FLOAT,
                concrete_mixture TEXT,
                concrete_mixture_quantity FLOAT,
                other_material TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')

        # Создание таблицы people_and_equipment_reports
        await db.execute('''
            CREATE TABLE IF NOT EXISTS people_and_equipment_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                create_datetime TEXT NOT NULL,
                is_uploaded_to_cloud BOOLEAN DEFAULT FALSE,
                upload_datetime TEXT,
                stage TEXT,
                date TEXT,
                people_number FLOAT,
                equipment_number FLOAT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')

        # Создание таблицы construction_projects
        await db.execute('''
            CREATE TABLE IF NOT EXISTS construction_projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                is_active BOOLEAN DEFAULT TRUE
            )
        ''')

        await db.commit()


async def main():
    await create_table()


if __name__ == '__main__':
    asyncio.run(main())