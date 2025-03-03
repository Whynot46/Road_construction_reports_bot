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


# Добавление нового пользователя
async def add_new_user(user_id, firstname, middlename, lastname):
    global db_connection
    await db_connection.execute('''
        INSERT INTO Users (user_id, firstname, middlename, lastname)
        VALUES (?, ?, ?, ?)
    ''', (user_id, firstname, middlename, lastname))
    await db_connection.commit()


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


async def get_report(report_id):
    global db_connection
    cursor = await db_connection.execute("SELECT * FROM reports WHERE id = ?", (report_id,))
    return await cursor.fetchone()


async def add_report(user_id, report_date, report_content, is_resolved=False):
    global db_connection
    await db_connection.execute('''
        INSERT INTO reports (user_id, report_date, report_content, is_resolved)
        VALUES (?, ?, ?, ?)
    ''', (user_id, report_date, report_content, is_resolved))
    await db_connection.commit()


async def get_preparatory_reports():
    global db_connection
    cursor = await db_connection.execute("SELECT * FROM preparatory_reports")
    return await cursor.fetchall()


async def get_preparatory_report(report_id):
    global db_connection
    cursor = await db_connection.execute("SELECT * FROM preparatory_reports WHERE id = ?", (report_id,))
    return await cursor.fetchone()


async def add_preparatory_report(user_id, is_uploaded_to_cloud=False, upload_datetime=None,
                                route_breakdown=None, clearing_way=None, water_disposal=None, water_disposal_scope=None,
                                removal_utility_networks=None, removal_utility_networks_scope=None,
                                temporary_construction=None, quarries_construction=None, quarries_construction_quantity=None,
                                cutting_asphalt_area=None, other_works=None, photo_links=None):
    global db_connection
    create_datetime = datetime.now().strftime("%Y-%m-%d %H:%M")
    await db_connection.execute('''
        INSERT INTO preparatory_reports (
            user_id, create_datetime, is_uploaded_to_cloud, upload_datetime, route_breakdown, clearing_way,
            water_disposal, water_disposal_scope, removal_utility_networks, removal_utility_networks_scope,
            temporary_construction, quarries_construction, quarries_construction_quantity, cutting_asphalt_area,
            other_works, photo_links
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, create_datetime, is_uploaded_to_cloud, upload_datetime, route_breakdown, clearing_way,
          water_disposal, water_disposal_scope, removal_utility_networks, removal_utility_networks_scope,
          temporary_construction, quarries_construction, quarries_construction_quantity, cutting_asphalt_area,
          other_works, photo_links))
    await db_connection.commit()


async def get_earthworks_reports():
    global db_connection
    cursor = await db_connection.execute("SELECT * FROM earthworks_reports")
    return await cursor.fetchall()


async def get_earthworks_report(report_id):
    global db_connection
    cursor = await db_connection.execute("SELECT * FROM earthworks_reports WHERE id = ?", (report_id,))
    return await cursor.fetchone()


async def add_earthworks_report(user_id, create_datetime, is_uploaded_to_cloud=False, upload_datetime=None,
                               detailed_breakdown=None, excavations_development=None, excavations_development_quantity=None,
                               soil_compaction=None, soil_compaction_quantity=None, final_layout=None, final_layout_quantity=None):
    global db_connection
    await db_connection.execute('''
        INSERT INTO earthworks_reports (
            user_id, create_datetime, is_uploaded_to_cloud, upload_datetime, detailed_breakdown, excavations_development,
            excavations_development_quantity, soil_compaction, soil_compaction_quantity, final_layout, final_layout_quantity
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, create_datetime, is_uploaded_to_cloud, upload_datetime, detailed_breakdown, excavations_development,
          excavations_development_quantity, soil_compaction, soil_compaction_quantity, final_layout, final_layout_quantity))
    await db_connection.commit()


async def get_artificial_structures_reports():
    global db_connection
    cursor = await db_connection.execute("SELECT * FROM artificial_structures_reports")
    return await cursor.fetchall()


async def get_artificial_structures_report(report_id):
    global db_connection
    cursor = await db_connection.execute("SELECT * FROM artificial_structures_reports WHERE id = ?", (report_id,))
    return await cursor.fetchone()


async def add_artificial_structures_report(user_id, create_datetime, is_uploaded_to_cloud=False, upload_datetime=None,
                                          work_type=None, work_scope=None):
    global db_connection
    await db_connection.execute('''
        INSERT INTO artificial_structures_reports (
            user_id, create_datetime, is_uploaded_to_cloud, upload_datetime, work_type, work_scope
        ) VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, create_datetime, is_uploaded_to_cloud, upload_datetime, work_type, work_scope))
    await db_connection.commit()


async def get_road_clothing_reports():
    global db_connection
    cursor = await db_connection.execute("SELECT * FROM road_clothing_reports")
    return await cursor.fetchall()


async def get_road_clothing_report(report_id):
    global db_connection
    cursor = await db_connection.execute("SELECT * FROM road_clothing_reports WHERE id = ?", (report_id,))
    return await cursor.fetchone()


async def add_road_clothing_report(user_id, create_datetime, is_uploaded_to_cloud=False, upload_datetime=None,
                                   underlying_layer=None, underlying_layer_area=None, additional_layer=None,
                                   additional_layer_area=None, foundation_construction=None, foundation_construction_area=None):
    global db_connection
    await db_connection.execute('''
        INSERT INTO road_clothing_reports (
            user_id, create_datetime, is_uploaded_to_cloud, upload_datetime, underlying_layer, underlying_layer_area,
            additional_layer, additional_layer_area, foundation_construction, foundation_construction_area
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, create_datetime, is_uploaded_to_cloud, upload_datetime, underlying_layer, underlying_layer_area,
          additional_layer, additional_layer_area, foundation_construction, foundation_construction_area))
    await db_connection.commit()


async def get_asphalt_clothing_reports():
    global db_connection
    cursor = await db_connection.execute("SELECT * FROM asphalt_clothing_reports")
    return await cursor.fetchall()


async def get_asphalt_clothing_report(report_id):
    global db_connection
    cursor = await db_connection.execute("SELECT * FROM asphalt_clothing_reports WHERE id = ?", (report_id,))
    return await cursor.fetchone()


async def add_asphalt_clothing_report(user_id, create_datetime, is_uploaded_to_cloud=False, upload_datetime=None,
                                      cleaning_base=None, cleaning_base_area=None, installation_primer=None,
                                      installation_primer_area=None, asphalt_mixture_lower=None, asphalt_mixture_lower_area=None,
                                      asphalt_mixture_upper=None, asphalt_mixture_upper_area=None):
    global db_connection
    await db_connection.execute('''
        INSERT INTO asphalt_clothing_reports (
            user_id, create_datetime, is_uploaded_to_cloud, upload_datetime, cleaning_base, cleaning_base_area,
            installation_primer, installation_primer_area, asphalt_mixture_lower, asphalt_mixture_lower_area,
            asphalt_mixture_upper, asphalt_mixture_upper_area
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, create_datetime, is_uploaded_to_cloud, upload_datetime, cleaning_base, cleaning_base_area,
          installation_primer, installation_primer_area, asphalt_mixture_lower, asphalt_mixture_lower_area,
          asphalt_mixture_upper, asphalt_mixture_upper_area))
    await db_connection.commit()


async def get_material_consumption_reports():
    global db_connection
    cursor = await db_connection.execute("SELECT * FROM material_consumption_reports")
    return await cursor.fetchall()


async def get_material_consumption_report(report_id):
    global db_connection
    cursor = await db_connection.execute("SELECT * FROM material_consumption_reports WHERE id = ?", (report_id,))
    return await cursor.fetchone()


async def add_material_consumption_report(user_id, create_datetime, is_uploaded_to_cloud=False, upload_datetime=None,
                                          stage=None, pgs_quantity=None, crushed_stone_fraction=None, crushed_stone_quantity=None,
                                          side_stone=None, side_stone_quantity=None, ebdc_quantity=None,
                                          asphalt_concrete_mixture=None, asphalt_concrete_scope=None, concrete_mixture=None,
                                          concrete_mixture_quantity=None, other_material=None):
    global db_connection
    await db_connection.execute('''
        INSERT INTO material_consumption_reports (
            user_id, create_datetime, is_uploaded_to_cloud, upload_datetime, stage, pgs_quantity, crushed_stone_fraction,
            crushed_stone_quantity, side_stone, side_stone_quantity, ebdc_quantity, asphalt_concrete_mixture,
            asphalt_concrete_scope, concrete_mixture, concrete_mixture_quantity, other_material
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, create_datetime, is_uploaded_to_cloud, upload_datetime, stage, pgs_quantity, crushed_stone_fraction,
          crushed_stone_quantity, side_stone, side_stone_quantity, ebdc_quantity, asphalt_concrete_mixture,
          asphalt_concrete_scope, concrete_mixture, concrete_mixture_quantity, other_material))
    await db_connection.commit()


async def get_people_and_equipment_reports():
    global db_connection
    cursor = await db_connection.execute("SELECT * FROM people_and_equipment_reports")
    return await cursor.fetchall()


async def get_people_and_equipment_report(report_id):
    global db_connection
    cursor = await db_connection.execute("SELECT * FROM people_and_equipment_reports WHERE id = ?", (report_id,))
    return await cursor.fetchone()


async def add_people_and_equipment_report(user_id, create_datetime, is_uploaded_to_cloud=False, upload_datetime=None,
                                          stage=None, date=None, people_number=None, equipment_number=None):
    global db_connection
    await db_connection.execute('''
        INSERT INTO people_and_equipment_reports (
            user_id, create_datetime, is_uploaded_to_cloud, upload_datetime, stage, date, people_number, equipment_number
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, create_datetime, is_uploaded_to_cloud, upload_datetime, stage, date, people_number, equipment_number))
    await db_connection.commit()


async def get_construction_projects():
    global db_connection
    cursor = await db_connection.execute("SELECT * FROM construction_projects")
    return await cursor.fetchall()


async def get_construction_project(project_id):
    global db_connection
    cursor = await db_connection.execute("SELECT * FROM construction_projects WHERE id = ?", (project_id,))
    return await cursor.fetchone()


async def add_construction_project(name, is_active=True):
    global db_connection
    await db_connection.execute('''
        INSERT INTO construction_projects (name, is_active)
        VALUES (?, ?)
    ''', (name, is_active))
    await db_connection.commit()