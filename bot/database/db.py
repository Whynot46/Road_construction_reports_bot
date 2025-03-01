import aiosqlite
from bot.config import Config

# Глобальная переменная для хранения соединения с базой данных
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

#Получить ФИО по user_id
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