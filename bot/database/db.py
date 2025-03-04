import aiosqlite
from bot.config import Config
from datetime import datetime

# Соединения с базой данных
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
        
        
async def update_user_id(user_id, firstname, middlename, lastname):
    global db_connection
    await db_connection.execute("UPDATE users SET user_id = ? WHERE firstname = ? AND middlename = ? AND lastname = ?"
                                , (user_id, firstname, middlename, lastname))
    await db_connection.commit()  
    
    
async def update_all_user_status(user_data):
    global db_connection
    if not user_data:
        print("Нет данных для обновления пользователей.")
        return

    for employee in user_data:
        full_name = employee["ФИО сотрудника"]
        status = employee["Статус"]

        lastname, firstname, middlename = full_name.split(" ")
        is_active = status == "Активный"

        # Проверяем, существует ли пользователь с таким ФИО
        cursor = await db_connection.execute(
            "SELECT user_id FROM Users WHERE firstname = ? AND middlename = ? AND lastname = ?",
            (firstname, middlename, lastname)
        )
        existing_user = await cursor.fetchone()

        if existing_user:
            await db_connection.execute(
                "UPDATE Users SET is_active = ? WHERE user_id = ?",
                (is_active, existing_user[0]))
        else:
            await db_connection.execute(
                "INSERT INTO Users (firstname, middlename, lastname, is_active) VALUES (?, ?, ?, ?)",
                (firstname, middlename, lastname, is_active))

    await db_connection.commit()
    
    
async def get_all_user_id() -> list:
    global db_connection
    cursor = await db_connection.execute('SELECT user_id FROM Users')
    rows = await cursor.fetchall()
    return [row[0] for row in rows]


# Получить ФИО пользователя по user_id
async def get_fullname(user_id):
    global db_connection
    cursor = await db_connection.execute('''SELECT firstname, middlename, lastname FROM Users WHERE user_id = ?''', (user_id,))
    result = await cursor.fetchone()
    if result:
        return f"{result[2]} {result[0]} {result[1]}"
    else:
        return None


# Проверка, зарегистрирован ли пользователь
async def is_old(user_id):
    global db_connection
    cursor = await db_connection.execute("SELECT 1 FROM Users WHERE user_id = ?", (user_id,))
    result = await cursor.fetchone()
    return bool(result)


async def is_active(user_id):
    global db_connection
    cursor = await db_connection.execute("SELECT 1 FROM Users WHERE user_id = ? AND is_active = 1", (user_id,))
    result = await cursor.fetchone()
    return bool(result)


async def add_photo_links(report_name, photo_links):
    global db_connection
    await db_connection.execute(f'''
                                INSERT INTO {report_name} ( photo_links)
                                VALUES (?)
                                ''', ( photo_links))
    await db_connection.commit()


async def get_construction_projects():
    global db_connection
    cursor = await db_connection.execute("SELECT * FROM construction_projects")
    return await cursor.fetchall()


async def get_construction_project(project_id):
    global db_connection
    cursor = await db_connection.execute("SELECT * FROM construction_projects WHERE id = ?", (project_id,))
    return await cursor.fetchone()


async def get_all_admins_id():
    global db_connection
    cursor = await db_connection.execute("SELECT user_id FROM Users WHERE is_admin = 1")
    rows = await cursor.fetchall()
    return [row[0] for row in rows]


async def update_construction_project(projects_data):
    global db_connection
    if not projects_data:
        print("Нет данных для обновления проектов.")
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