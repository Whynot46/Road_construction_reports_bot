import aiosqlite
from bot.config import Config
from datetime import datetime


db_connection = None


# Инициализация соединения с базой данных
async def init_db():
    global db_connection
    db_connection = await aiosqlite.connect(Config.DB_URL)


# Закрытие соединения с базой данных
async def close_db():
    global db_connection
    if db_connection:
        await db_connection.close()


#Сохранить id авторизованного пользователя 
async def update_user_id(user_id : int, firstname : str, middlename : str, lastname : str):
    global db_connection
    await db_connection.execute("UPDATE users SET user_id = ? WHERE firstname = ? AND middlename = ? AND lastname = ?"
                                , (user_id, firstname, middlename, lastname))
    await db_connection.commit()  
    

#Обновить статусы всех пользователей    
async def update_all_user_status(user_data : dict):
    global db_connection
    if not user_data:
        return

    for employee in user_data:
        full_name = employee["ФИО сотрудника"]
        status = employee["Статус"]

        lastname, firstname, middlename = full_name.split(" ")
        is_active = status == "Активный"

        # Проверяем, существует ли пользователь с таким ФИО
        cursor = await db_connection.execute(
            "SELECT user_id FROM users WHERE firstname = ? AND middlename = ? AND lastname = ?",
            (firstname, middlename, lastname)
        )
        existing_user = await cursor.fetchone()

        if existing_user:
            await db_connection.execute(
                "UPDATE users SET is_active = ? WHERE user_id = ?",
                (is_active, existing_user[0]))
        else:
            await db_connection.execute(
                "INSERT INTO users (firstname, middlename, lastname, is_active) VALUES (?, ?, ?, ?)",
                (firstname, middlename, lastname, is_active))

    await db_connection.commit()
    

#Получить id всех пользователей   
async def get_all_user_id() -> list:
    global db_connection
    cursor = await db_connection.execute('SELECT user_id FROM users')
    rows = await cursor.fetchall()
    return [row[0] for row in rows]


# Получить ФИО пользователя по user_id
async def get_fullname(user_id : int) -> str:
    global db_connection
    cursor = await db_connection.execute('''SELECT firstname, middlename, lastname FROM users WHERE user_id = ?''', (user_id,))
    result = await cursor.fetchone()
    if result:
        return f"{result[2]} {result[0]} {result[1]}"
    else:
        return None


# Проверка, зарегистрирован ли пользователь
async def is_old(user_id):
    global db_connection
    cursor = await db_connection.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,))
    result = await cursor.fetchone()
    return bool(result)


#Проверка, активен ли пользователь
async def is_user_active(user_id : int):
    global db_connection
    cursor = await db_connection.execute("SELECT 1 FROM users WHERE user_id = ? AND is_active = 1", (user_id,))
    result = await cursor.fetchone()
    return bool(result)


#Получить все объекты (проекты дорожно-строительной компании)
async def get_construction_projects() -> list:
    global db_connection
    cursor = await db_connection.execute("SELECT * FROM construction_projects")
    return await cursor.fetchall()


async def get_construction_project(project_id : id) -> dict:
    global db_connection
    cursor = await db_connection.execute("SELECT * FROM construction_projects WHERE id = ?", (project_id,))
    return await cursor.fetchone()


async def get_all_admins_id() -> list:
    global db_connection
    cursor = await db_connection.execute("SELECT user_id FROM users WHERE is_admin = 1")
    rows = await cursor.fetchall()
    return [row[0] for row in rows]


#Получить невыгруженные отчёты
async def get_not_uploaded_reports() -> list:
    global db_connection
    not_uploaded_reports = []

    # Список таблиц с отчётами
    report_tables = [
        "preparatory_reports",
        "earthworks_reports",
        "artificial_structures_reports",
        "road_clothing_reports",
        "asphalt_clothing_reports",
        "road_devices_reports"
    ]

    for table_name in report_tables:
        
        cursor = await db_connection.execute(f"""SELECT * FROM {table_name} WHERE is_uploaded_to_cloud = FALSE""")
        rows = await cursor.fetchall()

        cursor = await db_connection.execute(f"PRAGMA table_info({table_name})")
        columns_info = await cursor.fetchall()
        columns = [column[1] for column in columns_info]

        for row in rows:
            report_data = dict(zip(columns, row))
            not_uploaded_reports.append({
                "report_name": table_name,
                "report_data": report_data
            })

    return not_uploaded_reports


async def mark_report_as_uploaded(report_name: str, create_datetime: str):
    global db_connection

    table_names = {
        "Подготовительные работы": "preparatory_reports",
        "Земляные работы": "earthworks_reports",
        "Искусственные сооружения": "artificial_structures_reports",
        "Дорожная одежда": "road_clothing_reports",
        "Асфальт": "asphalt_clothing_reports",
        "Дорожные устройства и обстановка дороги": "road_devices_reports"
        }
    await db_connection.execute(
        f"""UPDATE {table_names[report_name]} 
            SET is_uploaded_to_cloud = TRUE 
            WHERE is_uploaded_to_cloud = FALSE 
            AND create_datetime = ?""",
        (create_datetime,)
    )
    await db_connection.commit()


async def update_construction_project(projects_data : dict) -> None:
    global db_connection
    if not projects_data:
        return

    for project in projects_data:
        project_name = project["Объект"]
        status = project["Статус"]

        is_active = status == "Активный"

        # Проверяем, существует ли проект с таким названием
        cursor = await db_connection.execute(
            "SELECT id FROM construction_projects WHERE name = ?",
            (project_name,))
        existing_project = await cursor.fetchone()

        if existing_project:
            # Обновляем статус существующего проекта
            await db_connection.execute(
                "UPDATE construction_projects SET is_active = ? WHERE id = ?",
                (is_active, existing_project[0]))
        else:
            # Создаем новый проект
            await db_connection.execute(
                "INSERT INTO construction_projects (name, is_active) VALUES (?, ?)",
                (project_name, is_active))

    await db_connection.commit()
    
    
async def add_preparatory_report(user_id, shift, project, create_datetime, route_breakdown, clearing_way, 
                                 water_disposal, water_disposal_scope, removal_utility_networks, removal_utility_networks_scope, 
                                 temporary_construction, quarries_construction, quarries_construction_quantity, cutting_asphalt_area, 
                                 other_works, photo_links, pgs_quantity, crushed_stone_fraction, crushed_stone_quantity, side_stone, 
                                 side_stone_quantity, ebdc_quantity, asphalt_concrete_mixture, asphalt_concrete_scope, concrete_mixture, 
                                 concrete_mixture_quantity, other_material, date, people_number, equipment_number):
    global db_connection
    await db_connection.execute('''
        INSERT INTO preparatory_reports (
            user_id, shift, project, create_datetime, is_uploaded_to_cloud, route_breakdown, clearing_way, 
            water_disposal, water_disposal_scope, removal_utility_networks, removal_utility_networks_scope, 
            temporary_construction, quarries_construction, quarries_construction_quantity, cutting_asphalt_area, 
            other_works, photo_links, pgs_quantity, crushed_stone_fraction, crushed_stone_quantity, side_stone, 
            side_stone_quantity, ebdc_quantity, asphalt_concrete_mixture, asphalt_concrete_scope, concrete_mixture, 
            concrete_mixture_quantity, other_material, date, people_number, equipment_number
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, shift, project, create_datetime, False, route_breakdown, clearing_way, 
          water_disposal, water_disposal_scope, removal_utility_networks, removal_utility_networks_scope, 
          temporary_construction, quarries_construction, quarries_construction_quantity, cutting_asphalt_area, 
          other_works, str(photo_links), pgs_quantity, crushed_stone_fraction, crushed_stone_quantity, side_stone, 
          side_stone_quantity, ebdc_quantity, asphalt_concrete_mixture, asphalt_concrete_scope, concrete_mixture, 
          concrete_mixture_quantity, other_material, date, people_number, equipment_number))
    await db_connection.commit()


async def add_earthworks_report(user_id, shift, project, create_datetime, detailed_breakdown, 
                                excavations_development, excavations_development_quantity, soil_compaction, soil_compaction_quantity, 
                                final_layout, final_layout_quantity, photo_links, pgs_quantity, crushed_stone_fraction, 
                                crushed_stone_quantity, side_stone, side_stone_quantity, ebdc_quantity, asphalt_concrete_mixture, 
                                asphalt_concrete_scope, concrete_mixture, concrete_mixture_quantity, other_material, date, 
                                people_number, equipment_number):
    global db_connection
    await db_connection.execute('''
        INSERT INTO earthworks_reports (
            user_id, shift, project, create_datetime, is_uploaded_to_cloud, detailed_breakdown, 
            excavations_development, excavations_development_quantity, soil_compaction, soil_compaction_quantity, 
            final_layout, final_layout_quantity, photo_links, pgs_quantity, crushed_stone_fraction, crushed_stone_quantity, 
            side_stone, side_stone_quantity, ebdc_quantity, asphalt_concrete_mixture, asphalt_concrete_scope, 
            concrete_mixture, concrete_mixture_quantity, other_material, date, people_number, equipment_number
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, shift, project, create_datetime, False, detailed_breakdown, 
          excavations_development, excavations_development_quantity, soil_compaction, soil_compaction_quantity, 
          final_layout, final_layout_quantity, str(photo_links), pgs_quantity, crushed_stone_fraction, crushed_stone_quantity, 
          side_stone, side_stone_quantity, ebdc_quantity, asphalt_concrete_mixture, asphalt_concrete_scope, 
          concrete_mixture, concrete_mixture_quantity, other_material, date, people_number, equipment_number))
    await db_connection.commit()


async def add_artificial_structures_report(user_id, shift, project, create_datetime, work_type, work_scope, 
                                           photo_links, pgs_quantity, crushed_stone_fraction, crushed_stone_quantity, side_stone, 
                                           side_stone_quantity, ebdc_quantity, asphalt_concrete_mixture, asphalt_concrete_scope, 
                                           concrete_mixture, concrete_mixture_quantity, other_material, date, people_number, equipment_number):
    global db_connection
    await db_connection.execute('''
        INSERT INTO artificial_structures_reports (
            user_id, shift, project, create_datetime, is_uploaded_to_cloud, work_type, work_scope, 
            photo_links, pgs_quantity, crushed_stone_fraction, crushed_stone_quantity, side_stone, 
            side_stone_quantity, ebdc_quantity, asphalt_concrete_mixture, asphalt_concrete_scope, 
            concrete_mixture, concrete_mixture_quantity, other_material, date, people_number, equipment_number
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, shift, project, create_datetime, False, work_type, work_scope, 
          str(photo_links), pgs_quantity, crushed_stone_fraction, crushed_stone_quantity, side_stone, 
          side_stone_quantity, ebdc_quantity, asphalt_concrete_mixture, asphalt_concrete_scope, 
          concrete_mixture, concrete_mixture_quantity, other_material, date, people_number, equipment_number))
    await db_connection.commit()


async def add_road_clothing_report(user_id, shift, project, create_datetime, underlying_layer, underlying_layer_area,
                                   additional_layer, additional_layer_area, foundation_construction, foundation_construction_area,
                                   photo_links, pgs_quantity, crushed_stone_fraction, crushed_stone_quantity, side_stone, side_stone_quantity,
                                   ebdc_quantity, asphalt_concrete_mixture, asphalt_concrete_scope, concrete_mixture, concrete_mixture_quantity,
                                   other_material, date, people_number, equipment_number):
    global db_connection
    await db_connection.execute('''
        INSERT INTO road_clothing_reports (
            user_id, shift, project, create_datetime, is_uploaded_to_cloud, underlying_layer, underlying_layer_area,
            additional_layer, additional_layer_area, foundation_construction, foundation_construction_area, 
            photo_links, pgs_quantity, crushed_stone_fraction, crushed_stone_quantity, side_stone, side_stone_quantity,
            ebdc_quantity, asphalt_concrete_mixture, asphalt_concrete_scope, concrete_mixture, concrete_mixture_quantity,
            other_material, date, people_number, equipment_number
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, shift, project, create_datetime, False, underlying_layer, underlying_layer_area,
          additional_layer, additional_layer_area, foundation_construction, foundation_construction_area,
          str(photo_links), pgs_quantity, crushed_stone_fraction, crushed_stone_quantity, side_stone, side_stone_quantity,
          ebdc_quantity, asphalt_concrete_mixture, asphalt_concrete_scope, concrete_mixture, concrete_mixture_quantity,
          other_material, date, people_number, equipment_number))
    await db_connection.commit()


async def add_asphalt_clothing_report(user_id, shift, project, create_datetime, cleaning_base, cleaning_base_area,
                                      installation_primer, installation_primer_area, asphalt_mixture_lower, asphalt_mixture_lower_area,
                                      asphalt_mixture_upper, asphalt_mixture_upper_area, photo_links, pgs_quantity, crushed_stone_fraction,
                                      crushed_stone_quantity, side_stone, side_stone_quantity, ebdc_quantity, asphalt_concrete_mixture,
                                      asphalt_concrete_scope, concrete_mixture, concrete_mixture_quantity, other_material, date, people_number,
                                      equipment_number):
    global db_connection
    await db_connection.execute('''
        INSERT INTO asphalt_clothing_reports (
            user_id, shift, project, create_datetime, is_uploaded_to_cloud, cleaning_base, cleaning_base_area,
            installation_primer, installation_primer_area, asphalt_mixture_lower, asphalt_mixture_lower_area,
            asphalt_mixture_upper, asphalt_mixture_upper_area, photo_links, pgs_quantity, crushed_stone_fraction,
            crushed_stone_quantity, side_stone, side_stone_quantity, ebdc_quantity, asphalt_concrete_mixture,
            asphalt_concrete_scope, concrete_mixture, concrete_mixture_quantity, other_material, date, people_number,
            equipment_number
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, shift, project, create_datetime, False, cleaning_base, cleaning_base_area,
          installation_primer, installation_primer_area, asphalt_mixture_lower, asphalt_mixture_lower_area,
          asphalt_mixture_upper, asphalt_mixture_upper_area, str(photo_links), pgs_quantity, crushed_stone_fraction,
          crushed_stone_quantity, side_stone, side_stone_quantity, ebdc_quantity, asphalt_concrete_mixture, asphalt_concrete_scope,
          concrete_mixture, concrete_mixture_quantity, other_material, date, people_number, equipment_number))
    await db_connection.commit()


async def add_road_devices_report(user_id, shift, project, create_datetime, characters_number,
                                  signal_posts_number, other_works, photo_links, pgs_quantity, crushed_stone_fraction,
                                  crushed_stone_quantity, side_stone, side_stone_quantity, ebdc_quantity, asphalt_concrete_mixture,
                                  asphalt_concrete_scope, concrete_mixture, concrete_mixture_quantity, other_material,
                                  date, people_number, equipment_number):
    global db_connection
    await db_connection.execute('''
        INSERT INTO road_devices_reports (
            user_id, shift, project, create_datetime, is_uploaded_to_cloud, characters_number,
            signal_posts_number, other_works, photo_links, pgs_quantity, crushed_stone_fraction,
                                crushed_stone_quantity, side_stone, side_stone_quantity, ebdc_quantity, asphalt_concrete_mixture,
                                asphalt_concrete_scope, concrete_mixture, concrete_mixture_quantity, other_material,
                                date, people_number, equipment_number
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, shift, project, create_datetime, False, characters_number,
          signal_posts_number, other_works, str(photo_links), pgs_quantity, crushed_stone_fraction,
          crushed_stone_quantity, side_stone, side_stone_quantity, ebdc_quantity, asphalt_concrete_mixture,
          asphalt_concrete_scope, concrete_mixture, concrete_mixture_quantity, other_material,
          date, people_number, equipment_number))
    await db_connection.commit()