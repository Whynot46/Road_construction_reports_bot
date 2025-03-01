from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup


def get_main_menu_keyboard():
    main_menu_keyboard = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text='Заполнить отчеты')]],
        resize_keyboard=True)
    return main_menu_keyboard


def get_shift_keyboard():
    shift_keyboard = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text='День'), 
        KeyboardButton(text='Ночь')]],
        resize_keyboard=True)
    return shift_keyboard


download_keyboard = track_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="download_keyboard", callback_data=f"was_download")]
    ])