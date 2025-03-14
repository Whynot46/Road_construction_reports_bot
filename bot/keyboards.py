from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
import bot.db as db

async def get_main_menu_keyboard():
    main_menu_keyboard = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text='Заполнить отчёты')]
    ], resize_keyboard=True)
    return main_menu_keyboard

async def get_start_keyboard():
    start_keyboard = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text='Старт')]
    ], resize_keyboard=True)
    return start_keyboard

async def get_report_keyboard():
    report_keyboard = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text='Отправить')],
        [KeyboardButton(text='Заполнить заново')]
    ], resize_keyboard=True)
    return report_keyboard

async def get_skip_keyboard():
    skip_keyboard = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text='Пропустить')]
    ], resize_keyboard=True)
    return skip_keyboard

async def get_none_work_keyboard():
    none_work_keyboard = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text='Работы не производились')]
    ], resize_keyboard=True)
    return none_work_keyboard

async def get_shift_keyboard():
    shift_keyboard = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text='День'), KeyboardButton(text='Ночь')]
    ], resize_keyboard=True)
    return shift_keyboard

async def get_report_chouse_keyboard():
    report_chouse_keyboard = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text='Отчёт по этапу работ')],
        [KeyboardButton(text='Отчёт по количеству людей и техники на объекте')]
    ], resize_keyboard=True)
    return report_chouse_keyboard

async def get_stage_keyboard():
    stage_keyboard = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text='Подготовительные работы')],
        [KeyboardButton(text='Земляные работы')],
        [KeyboardButton(text='Искусственные сооружения')],
        [KeyboardButton(text='Дорожная одежда')],
        [KeyboardButton(text='Асфальт')],
        [KeyboardButton(text='Дорожные устройства и обстановка дороги')]
    ], resize_keyboard=True)
    return stage_keyboard

async def get_project_keyboard():
    projects = await db.get_construction_projects()
    if len(projects) > 0:
        projects_buttons = []
        for project in projects:
            if project[2]:
                projects_buttons.append([KeyboardButton(text=project[1])])
        project_keyboard = ReplyKeyboardMarkup(keyboard=projects_buttons, resize_keyboard=True)
        return project_keyboard
    else:
        return ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text='В справочнике нет объектов')]
        ], resize_keyboard=True)

async def remove_keyboard():
    return ReplyKeyboardRemove()

async def get_add_material_keyboard():
    add_material_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Добавить материал")],
            [KeyboardButton(text="Перейти к следующему вопросу")]
        ],
        resize_keyboard=True
    )
    return add_material_keyboard

async def get_add_work_keyboard():
    add_work_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Добавить ещё работы")],
            [KeyboardButton(text="Перейти к следующему вопросу")]
        ],
        resize_keyboard=True
    )
    return add_work_keyboard