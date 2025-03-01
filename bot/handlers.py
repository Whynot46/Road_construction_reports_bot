from aiogram.filters.command import Command
from aiogram import F, Bot
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram import Router
from aiogram.fsm.context import FSMContext
import bot.keyboards as kb
import bot.database.db as db
import bot.services.yandex_disk_service as yadisk
from bot.states import *


router = Router()


@router.message(F.text, Command("start"))
async def start_loop(message: Message, state = FSMContext):
    if not await db.is_old(message.from_user.id):
        await state.set_state(Register_steps.fullname)
        await message.answer("Введи своё ФИО:")
    else:
        user_fullname = await db.get_fullname(message.from_user.id)
        await message.answer(f"Приветствую Вас, старик {user_fullname}!", reply_markup=kb.get_main_menu_keyboard())
    

@router.message(Register_steps.fullname)
async def fullname_loop(message: Message, state: FSMContext):
    await state.update_data(fullname=message.text)
    fullname = await state.get_data()
    if await yadisk.is_user_in_reference_table(fullname):
        await db.add_new_user(message.from_user.id, message.from_user.username, message.from_user.username, message.from_user.username)
        await message.answer(f"Приветствую Вас, {fullname}!", reply_markup=kb.get_main_menu_keyboard())
            
        
@router.message(F.text == "Заполнить отчеты")  
async def find_track(message: Message, bot: Bot, state = FSMContext):  
    await message.answer("Выберите смену", reply_markup=kb.get_shift_keyboard())
    

@router.callback_query(F.data)
async def track_callback(callback: CallbackQuery, bot: Bot):
    pass