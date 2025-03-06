from aiogram.filters.command import Command
from aiogram import F, Bot
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram import Router
from aiogram.fsm.context import FSMContext
import bot.keyboards as kb
import bot.database.db as db
import bot.services.google_api_service as google_disk
from bot.states import *
from datetime import datetime
import os
import asyncio
import re
from config import Config


router = Router()


@router.message(F.text, Command("start"))
async def start_loop(message: Message, state = FSMContext):
    if not await db.is_old(message.from_user.id):
        await state.set_state(Register_steps.fullname)
        await message.answer("Введи своё ФИО:")
    else:
        if await db.is_active(message.from_user.id):
            user_fullname = await db.get_fullname(message.from_user.id)
            await message.answer(f"Приветствую Вас, старик {user_fullname}!", reply_markup= await kb.get_main_menu_keyboard())
        else:
            await message.answer(f"Администратор деактивировал ваш аккаунт", reply_markup= await kb.remove_keyboard())


@router.message(Register_steps.fullname)
async def registration(message: Message, state: FSMContext):
    await state.update_data(fullname=message.text)
    fullname = await state.get_data()
    lastname, firstname, middlename = fullname.split(" ")
    await db.update_user_id(message.from_user.id, firstname, middlename, lastname)
    await message.answer(f"Приветствую Вас, {fullname}!", reply_markup= await kb.get_main_menu_keyboard())
    await state.clear()

            
@router.message(F.text == "Заполнить отчеты")  
async def chouse_shift(message: Message, state = FSMContext):  
    await state.set_state(Construction_projects_steps.shift)
    await message.answer("Выберите смену", reply_markup= await kb.get_shift_keyboard())


@router.message(Construction_projects_steps.shift)
async def chouse_project(message: Message, state: FSMContext):
    await state.update_data(shift=message.text)
    await state.set_state(Construction_projects_steps.project)
    await message.answer("Выберите объект", reply_markup= await kb.get_project_keyboard())


@router.message(Construction_projects_steps.project)
async def chouse_stage(message: Message, state: FSMContext):
    await state.update_data(project=message.text)
    await state.set_state(Construction_projects_steps.stage)
    await message.answer("Выберите этап работ", reply_markup= await kb.get_stage_keyboard())


@router.message(Construction_projects_steps.stage)
async def set_route_breakdown(message: Message, state: FSMContext):
    await state.update_data(stage=message.text)
    if message.text=="Подготовительные работы":
        await state.set_state(Preparatory_steps.route_breakdown)
        await message.answer("Разбивка трассы. Укажите количество км.", reply_markup= await kb.remove_keyboard())
    elif message.text=="Земляные работы":
        await state.set_state(Earthworks_steps.detailed_breakdown)
        await message.answer("Детальная разбивка элементов дороги и подготовка основания Укажите с какого ПК по какой ПК в формате: 1+00-2+00", reply_markup= await kb.remove_keyboard())
    elif message.text=="Искусственные сооружения":
        await state.set_state(Artificial_structures_steps.work_type)
        await message.answer("Укажите вид работ.", reply_markup= await kb.remove_keyboard())
    elif message.text=="Дорожная одежда":
        await state.set_state(Road_clothing_steps.underlying_layer)
        await message.answer("Подстилающий слой из песка. Укажите с какого ПК по какой ПК в формате: 1+00-2+00.", reply_markup= await kb.remove_keyboard())
    elif message.text=="Асфальт":
        await state.set_state(Asphalt_steps.cleaning_base)
        await message.answer("Очистка основания от пыли и грязи механизированным способом. Укажите с какого ПК по какой ПК в формате: 1+00-2+00.", reply_markup= await kb.remove_keyboard())
    elif message.text=="Дорожные устройства и обстановка дороги":
        await state.set_state(Road_devices_steps.characters_number)
        await message.answer("Напишите нумерацию  и количество знаков, установленных за сегодня, в формате 3.24 - 5", reply_markup= await kb.remove_keyboard())
    
    
@router.message(Preparatory_steps.route_breakdown)
async def set_clearing_way(message: Message, state: FSMContext):
    if (message.text).isdigit():
        await state.update_data(route_breakdown=message.text)
        await state.set_state(Preparatory_steps.clearing_way)
        await message.answer("Расчистка полосы отвода. Укажите количество км.", reply_markup= await kb.remove_keyboard())
    else:
        await state.set_state(Preparatory_steps.route_breakdown)
        await message.answer("Необходимо указать число!", reply_markup= await kb.remove_keyboard())
    
    
@router.message(Preparatory_steps.clearing_way)
async def set_water_disposal(message: Message, state: FSMContext):
    if (message.text).isdigit():
        await state.update_data(clearing_way=message.text)
        await state.set_state(Preparatory_steps.water_disposal)
        await message.answer("Водоотведение и временное водопонижение. Укажите вид работ.", reply_markup= await kb.remove_keyboard())
    else:
        await state.set_state(Preparatory_steps.clearing_way)
        await message.answer("Необходимо указать число!", reply_markup= await kb.remove_keyboard())
    
    
@router.message(Preparatory_steps.water_disposal)
async def set_water_disposal_scope(message: Message, state: FSMContext):
    await state.update_data(water_disposal=message.text)
    await state.set_state(Preparatory_steps.water_disposal_scope)
    await message.answer("Водоотведение и временное водопонижение. Укажите объем работ.", reply_markup= await kb.remove_keyboard())
    
    
@router.message(Preparatory_steps.water_disposal_scope)
async def set_removal_utility_networks(message: Message, state: FSMContext):
    await state.update_data(water_disposal_scope=message.text)
    await state.set_state(Preparatory_steps.removal_utility_networks)
    await message.answer("Вынос инженерных сетей и снос зданий и сооружений. Укажите вид работ.", reply_markup= await kb.remove_keyboard())
    
    
@router.message(Preparatory_steps.removal_utility_networks)
async def set_removal_utility_networks_scope(message: Message, state: FSMContext):
    await state.update_data(removal_utility_networks=message.text)
    await state.set_state(Preparatory_steps.removal_utility_networks_scope)
    await message.answer("Вынос инженерных сетей и снос зданий и сооружений. Укажите объем работ.", reply_markup= await kb.remove_keyboard())
    
    
@router.message(Preparatory_steps.removal_utility_networks_scope)
async def set_removal_temporary_construction(message: Message, state: FSMContext):
    await state.update_data(removal_utility_networks_scope=message.text)
    await state.set_state(Preparatory_steps.temporary_construction)
    await message.answer("Устройство временных автодорог и объездов. Укажите количество км.", reply_markup= await kb.remove_keyboard())
    
    
@router.message(Preparatory_steps.temporary_construction)
async def set_quarries_construction(message: Message, state: FSMContext):
    if (message.text).isdigit():
        await state.update_data(temporary_construction=message.text)
        await state.set_state(Preparatory_steps.quarries_construction)
        await message.answer("Устройство карьеров и резервов. Укажите какой материал привезли?", reply_markup= await kb.remove_keyboard())
    else:
        await state.set_state(Preparatory_steps.temporary_construction)
        await message.answer("Необходимо указать число!", reply_markup= await kb.remove_keyboard())
        
    
@router.message(Preparatory_steps.quarries_construction)
async def set_quarries_construction_quantity(message: Message, state: FSMContext):
    await state.update_data(quarries_construction=message.text)
    await state.set_state(Preparatory_steps.quarries_construction_quantity)
    await message.answer("Устройство карьеров и резервов. Укажите количество в тоннах.", reply_markup= await kb.remove_keyboard())
    

@router.message(Preparatory_steps.quarries_construction_quantity)
async def set_cutting_asphalt_area(message: Message, state: FSMContext):
    if (message.text).isdigit():
        await state.update_data(quarries_construction_quantity=message.text)
        await state.set_state(Preparatory_steps.cutting_asphalt_area)
        await message.answer("Срезка асфальтобетонного покрытия методом холодного фрезерования. Укажите площадь в м².", reply_markup= await kb.remove_keyboard())
    else:
        await state.set_state(Preparatory_steps.quarries_construction_quantity)
        await message.answer("Необходимо указать число!", reply_markup= await kb.remove_keyboard())

@router.message(Preparatory_steps.cutting_asphalt_area)
async def set_cutting_asphalt_area(message: Message, state: FSMContext):
    if (message.text).isdigit():
        await state.update_data(cutting_asphalt_area=message.text)
        await state.set_state(Preparatory_steps.other_works)
        await message.answer("Другие работы? Опишите.", reply_markup= await kb.remove_keyboard())
    else:
        await state.set_state(Preparatory_steps.cutting_asphalt_area)
        await message.answer("Необходимо указать число!", reply_markup= await kb.remove_keyboard())
    

@router.message(Preparatory_steps.other_works)
async def set_photo_links(message: Message, state: FSMContext):
    await state.update_data(other_works=message.text)
    await state.set_state(Preparatory_steps.photo_links)
    await message.answer("Прикрепить 5 четких фото по этому виду работ", reply_markup= await kb.remove_keyboard())
    

@router.message(Preparatory_steps.photo_links)
async def set_other_works(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()

    if "photo_links" not in data:
        data["photo_links"] = []

    if type(data["photo_links"]) == str:
        data["photo_links"] = []

    if message.photo:
        photo_file_id = message.photo[-1].file_id
        data["photo_links"].append(photo_file_id)

    await state.update_data(photo_links=data["photo_links"])

    if len(data["photo_links"]) >= 5:
        await message.answer("⏳Загрузка прикрепленных фото в облако...")
        photo_file_names = await download_photos("Preparatory", data["photo_links"], message.from_user.id, bot)
        photo_file_names_str = "./media\n".join(photo_file_names)
        await state.update_data(photo_links=photo_file_names_str)

        files_url = []
        for file_name in photo_file_names:
            file_url = await google_disk.upload_file(f"./bot/media/{file_name}")
            files_url.append(file_url)
        files_url_str = "\n".join(files_url)

        await state.update_data(photo_links=files_url_str)
        
        report_data = await state.get_data()
        await message.answer("✅Фото успешно загружены!")
        await state.set_state(Preparatory_steps.is_ok)
        await message.answer(f"Отчету по этапу {report_data['stage']}:\n\n"
                        f"Смена: {report_data['shift']}\n"
                        f"Объект: {report_data['project']}\n"
                        f"Разбивка трассы. Количество км.: {report_data['route_breakdown']}\n"
                        f"Расчистка полосы отвода. Количество км.: {report_data['clearing_way']}\n"
                        f"Водоотведение и временное водопонижение. Вид работ: {report_data['water_disposal']}\n"
                        f"Водоотведение и временное водопонижение. Объем работ: {report_data['water_disposal_scope']}\n"
                        f"Вынос инженерных сетей и снос зданий и сооружений. Вид работ: {report_data['removal_utility_networks']}\n"
                        f"Вынос инженерных сетей и снос зданий и сооружений. Объем работ: {report_data['removal_utility_networks_scope']}\n"
                        f"Устройство временных автодорог и объездов. Количество км.: {report_data['temporary_construction']}\n"
                        f"Устройство карьеров и резервов. Материал: {report_data['quarries_construction']}\n"
                        f"Устройство карьеров и резервов. Количество в тоннах: {report_data['quarries_construction_quantity']}\n"
                        f"Срезка асфальтобетонного покрытия методом холодного фрезерования. Площадь в м²: {report_data['cutting_asphalt_area']}\n"
                        f"Другие работы: Площадь в м²: {report_data['other_works']}\n"
                        f"Ссылки на фото:\n{report_data['photo_links']}\n"
                        , reply_markup= await kb.get_report_keyboard())


@router.message(Preparatory_steps.is_ok)
async def set_photo_links(message: Message, state: FSMContext):
    await state.update_data(is_ok=message.text)
    if message.text == "Заполнить заново":
        await state.set_state(Preparatory_steps.route_breakdown)
        await message.answer("Разбивка трассы. Укажите количество км.", reply_markup= await kb.remove_keyboard())
    elif message.text == "Отправить":
        await state.set_state(Material_consumption_report_steps.pgs_quantity)
        await message.answer("ПГС. Укажите количество тонн.", reply_markup=await kb.remove_keyboard())
    else:
        await state.set_state(Preparatory_steps.is_ok)
        await message.answer("Неизвестная команда", reply_markup=await kb.get_report_keyboard())
        
        
@router.message(Earthworks_steps.detailed_breakdown)
async def set_photo_links(message: Message, state: FSMContext):
    if re.match(r"(\d+)\+(\d+)-(\d+)\+(\d+)", message.text):
        await state.update_data(detailed_breakdown=message.text)
        await state.set_state(Earthworks_steps.excavations_development)
        await message.answer("Разработка выемок и возведение насыпей. Укажите вид работ.", reply_markup= await kb.remove_keyboard())
    else:
        await state.set_state(Earthworks_steps.detailed_breakdown)
        await message.answer("Необходимо ввести значение в формате 1+00-2+00!", reply_markup= await kb.remove_keyboard())
    

@router.message(Earthworks_steps.excavations_development)
async def set_photo_links(message: Message, state: FSMContext):
    await state.update_data(excavations_development=message.text)
    await state.set_state(Earthworks_steps.excavations_development_quantity)
    await message.answer("Разработка выемок и возведение насыпей. Укажите количество в м3.", reply_markup= await kb.remove_keyboard())
    

@router.message(Earthworks_steps.excavations_development_quantity)
async def set_photo_links(message: Message, state: FSMContext):
    if (message.text).isdigit():
        await state.update_data(excavations_development_quantity=message.text)
        await state.set_state(Earthworks_steps.soil_compaction)
        await message.answer("Уплотнение грунта. Укажите с какого ПК по какой ПК в формате: 1+00-2+00", reply_markup= await kb.remove_keyboard())
    else:
        await state.set_state(Earthworks_steps.excavations_development_quantity)
        await message.answer("Необходимо указать число!", reply_markup= await kb.remove_keyboard())
    

@router.message(Earthworks_steps.soil_compaction)
async def set_photo_links(message: Message, state: FSMContext):
    if re.match(r"(\d+)\+(\d+)-(\d+)\+(\d+)", message.text):
        await state.update_data(soil_compaction=message.text)
        await state.set_state(Earthworks_steps.soil_compaction_quantity)
        await message.answer("Уплотнение грунта. Укажите количество в м3.", reply_markup= await kb.remove_keyboard())
    else:
        await state.set_state(Earthworks_steps.soil_compaction)
        await message.answer("Необходимо ввести значение в формате 1+00-2+00!", reply_markup= await kb.remove_keyboard())
    

@router.message(Earthworks_steps.soil_compaction_quantity)
async def set_photo_links(message: Message, state: FSMContext):
    if (message.text).isdigit():
        await state.update_data(soil_compaction_quantity=message.text)
        await state.set_state(Earthworks_steps.final_layout)
        await message.answer("Окончательная планировка.  Укажите с какого ПК по какой ПК в формате: 1+00-2+00", reply_markup= await kb.remove_keyboard())
    else:
        await state.set_state(Earthworks_steps.soil_compaction_quantity)
        await message.answer("Необходимо указать число!", reply_markup= await kb.remove_keyboard())


@router.message(Earthworks_steps.final_layout)
async def set_photo_links(message: Message, state: FSMContext):
    if re.match(r"(\d+)\+(\d+)-(\d+)\+(\d+)", message.text):
        await state.update_data(final_layout=message.text)
        await state.set_state(Earthworks_steps.final_layout_quantity)
        await message.answer("Окончательная планировка. Укажите количество в м2.", reply_markup= await kb.remove_keyboard())
    else:
        await state.set_state(Earthworks_steps.final_layout)
        await message.answer("Необходимо ввести значение в формате 1+00-2+00!", reply_markup= await kb.remove_keyboard())
        
    
@router.message(Earthworks_steps.final_layout_quantity)
async def set_photo_links(message: Message, state: FSMContext):
    if (message.text).isdigit():
        await state.update_data(final_layout_quantity=message.text)
        await state.set_state(Earthworks_steps.photo_links)
        await message.answer("Прикрепить 5 четких фото по этому виду работ", reply_markup= await kb.remove_keyboard())
    else:
        await state.set_state(Earthworks_steps.final_layout_quantity)
        await message.answer("Необходимо указать число!", reply_markup= await kb.remove_keyboard()) 


@router.message(Earthworks_steps.photo_links)
async def set_other_works(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()

    if "photo_links" not in data:
        data["photo_links"] = []

    if message.photo:
        photo_file_id = message.photo[-1].file_id
        data["photo_links"].append(photo_file_id)

    await state.update_data(photo_links=data["photo_links"])

    if len(data["photo_links"]) >= 5:
        await message.answer("⏳Загрузка прикрепленных фото в облако...")
        photo_file_names = await download_photos("Earthworks", data["photo_links"], message.from_user.id, bot)
        photo_file_names_str = "./media\n".join(photo_file_names)
        await state.update_data(photo_links=photo_file_names_str)

        files_url = []
        for file_name in photo_file_names:
            file_url = await google_disk.upload_file(f"./bot/media/{file_name}")
            files_url.append(file_url)
        files_url_str = "\n".join(files_url)

        await state.update_data(photo_links=files_url_str)

        report_data = await state.get_data()
        await message.answer("✅Фото успешно загружены!")
        await state.set_state(Earthworks_steps.is_ok)
        await message.answer(f"Отчету по этапу {report_data['stage']}:\n\n"
                        f"Смена: {report_data['shift']}\n"
                        f"Объект: {report_data['project']}\n"
                        f"Детальная разбивка элементов дороги и подготовка основания. С какого ПК по какой ПК в формате: 1+00-2+00: {report_data['detailed_breakdown']}\n"
                        f"Разработка выемок и возведение насыпей. Вид работ: {report_data['excavations_development']}\n"
                        f"Водоотведение и временное водопонижение. Вид работ: {report_data['excavations_development_quantity']}\n"
                        f"Разработка выемок и возведение насыпей. Количество в м3: {report_data['excavations_development_quantity']}\n"
                        f"Уплотнение грунта. С какого ПК по какой ПК в формате: 1+00-2+00: {report_data['soil_compaction']}\n"
                        f"Уплотнение грунта. Количество в м3: {report_data['soil_compaction_quantity']}\n"
                        f"Окончательная планировка. С какого ПК по какой ПК в формате: 1+00-2+00: {report_data['final_layout']}\n"
                        f"Окончательная планировка. Количество в м2: {report_data['final_layout_quantity']}\n"
                        f"Ссылки на фото:\n{report_data['photo_links']}\n"
                        , reply_markup= await kb.get_report_keyboard())
        
        
@router.message(Earthworks_steps.is_ok)
async def set_photo_links(message: Message, state: FSMContext):
    await state.update_data(is_ok=message.text)
    if message.text == "Заполнить заново":
        await state.set_state(Earthworks_steps.excavations_development)
        await message.answer("Детальная разбивка элементов дороги и подготовка основания Укажите с какого ПК по какой ПК в формате: 1+00-2+00", reply_markup= await kb.remove_keyboard())
    elif message.text == "Отправить":
        await state.set_state(Material_consumption_report_steps.pgs_quantity)
        await message.answer("ПГС. Укажите количество тонн.", reply_markup=await kb.remove_keyboard())
    else:
        await state.set_state(Earthworks_steps.is_ok)
        await message.answer("Неизвестная команда", reply_markup=await kb.get_report_keyboard())


@router.message(Artificial_structures_steps.work_type)
async def set_photo_links(message: Message, state: FSMContext):
    await state.update_data(work_type=message.text)
    await state.set_state(Artificial_structures_steps.work_scope)
    await message.answer("Укажите объем работ.", reply_markup= await kb.remove_keyboard())
    
    
@router.message(Artificial_structures_steps.work_scope)
async def set_photo_links(message: Message, state: FSMContext):
    await state.update_data(work_scope=message.text)
    await state.set_state(Artificial_structures_steps.photo_links)
    await message.answer("Прикрепить 5 четких фото по этому виду работ", reply_markup= await kb.remove_keyboard())
    
    
@router.message(Artificial_structures_steps.photo_links)
async def set_other_works(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()

    if "photo_links" not in data:
        data["photo_links"] = []

    if message.photo:
        photo_file_id = message.photo[-1].file_id
        data["photo_links"].append(photo_file_id)

    await state.update_data(photo_links=data["photo_links"])

    if len(data["photo_links"]) >= 5:
        await message.answer("⏳Загрузка прикрепленных фото в облако...")
        photo_file_names = await download_photos("Artificial_structures", data["photo_links"], message.from_user.id, bot)
        photo_file_names_str = "./media\n".join(photo_file_names)
        await state.update_data(photo_links=photo_file_names_str)

        files_url = []
        for file_name in photo_file_names:
            file_url = await google_disk.upload_file(f"./bot/media/{file_name}")
            files_url.append(file_url)
        files_url_str = "\n".join(files_url)

        await state.update_data(photo_links=files_url_str)

        report_data = await state.get_data()
        await message.answer("✅Фото успешно загружены!")
        await state.set_state(Artificial_structures_steps.is_ok)
        await message.answer(f"Отчету по этапу {report_data['stage']}:\n\n"
                        f"Смена: {report_data['shift']}\n"
                        f"Объект: {report_data['project']}\n"
                        f"Вид работ: {report_data['work_type']}\n"
                        f"Объем работ: {report_data['work_scope']}\n"
                        f"Ссылки на фото:\n{report_data['photo_links']}\n"
                        , reply_markup= await kb.get_report_keyboard())
        
        
@router.message(Artificial_structures_steps.is_ok)
async def set_photo_links(message: Message, state: FSMContext):
    await state.update_data(is_ok=message.text)
    if message.text == "Заполнить заново":
        await state.set_state(Artificial_structures_steps.work_type)
        await message.answer("Укажите вид работ.", reply_markup= await kb.remove_keyboard())
    elif message.text == "Отправить":
        await state.set_state(Material_consumption_report_steps.pgs_quantity)
        await message.answer("ПГС. Укажите количество тонн.", reply_markup=await kb.remove_keyboard())
    else:
        await state.set_state(Artificial_structures_steps.is_ok)
        await message.answer("Неизвестная команда", reply_markup=await kb.get_report_keyboard())
        
        
@router.message(Road_clothing_steps.underlying_layer)
async def set_photo_links(message: Message, state: FSMContext):
    if re.match(r"(\d+)\+(\d+)-(\d+)\+(\d+)", message.text):
        await state.update_data(underlying_layer=message.text)
        await state.set_state(Road_clothing_steps.underlying_layer_area)
        await message.answer("Подстилающий слой из песка. Укажите количество площадь/толщина.", reply_markup= await kb.remove_keyboard())
    else:
        await state.set_state(Road_clothing_steps.underlying_layer)
        await message.answer("Необходимо ввести значение в формате 1+00-2+00!", reply_markup= await kb.remove_keyboard())
        
    
@router.message(Road_clothing_steps.underlying_layer_area)
async def set_photo_links(message: Message, state: FSMContext):
    if re.match(r"\d+\/\s?\d+", message.text): 
        await state.update_data(underlying_layer_area=message.text)
        await state.set_state(Road_clothing_steps.additional_layer)
        await message.answer("Дополнительный слой из ПГС. Укажите с какого ПК по какой ПК в формате: 1+00-2+00.", reply_markup= await kb.remove_keyboard())
    else:
        await state.set_state(Road_clothing_steps.underlying_layer_area)
        await message.answer("Необходимо ввести значение в формате число/число", reply_markup= await kb.remove_keyboard()) 
        
    
@router.message(Road_clothing_steps.additional_layer)
async def set_photo_links(message: Message, state: FSMContext):
    if re.match(r"(\d+)\+(\d+)-(\d+)\+(\d+)", message.text):
        await state.update_data(additional_layer=message.text)
        await state.set_state(Road_clothing_steps.additional_layer_area)
        await message.answer("Дополнительный слой из ПГС. Укажите количество площадь/толщина.", reply_markup= await kb.remove_keyboard())
    else:
        await state.set_state(Road_clothing_steps.additional_layer)
        await message.answer("Необходимо ввести значение в формате 1+00-2+00!", reply_markup= await kb.remove_keyboard())
    
    
@router.message(Road_clothing_steps.additional_layer_area)
async def set_photo_links(message: Message, state: FSMContext):
    if re.match(r"\d+\/\s?\d+", message.text): 
        await state.update_data(additional_layer_area=message.text)
        await state.set_state(Road_clothing_steps.foundation_construction)
        await message.answer("Устройство основания из щебня. Укажите с какого ПК по какой ПК в формате: 1+00-2+00.", reply_markup= await kb.remove_keyboard())
    else:
        await state.set_state(Road_clothing_steps.additional_layer_area)
        await message.answer("Необходимо ввести значение в формате число/число", reply_markup= await kb.remove_keyboard()) 
    
    
@router.message(Road_clothing_steps.foundation_construction)
async def set_photo_links(message: Message, state: FSMContext):
    if re.match(r"(\d+)\+(\d+)-(\d+)\+(\d+)", message.text):
        await state.update_data(foundation_construction=message.text)
        await state.set_state(Road_clothing_steps.foundation_construction_area)
        await message.answer("Устройство основания из щебня. Укажите количество площадь/толщина.", reply_markup= await kb.remove_keyboard())
    else:
        await state.set_state(Road_clothing_steps.foundation_construction)
        await message.answer("Необходимо ввести значение в формате 1+00-2+00!", reply_markup= await kb.remove_keyboard())

@router.message(Road_clothing_steps.foundation_construction_area)
async def set_photo_links(message: Message, state: FSMContext):
    if re.match(r"\d+\/\s?\d+", message.text): 
        await state.update_data(foundation_construction_area=message.text)
        await state.set_state(Road_clothing_steps.photo_links)
        await message.answer("Прикрепить 5 четких фото по этому виду работ", reply_markup= await kb.remove_keyboard())
    else:
        await state.set_state(Road_clothing_steps.foundation_construction_area)
        await message.answer("Необходимо ввести значение в формате число/число", reply_markup= await kb.remove_keyboard()) 


@router.message(Road_clothing_steps.photo_links)
async def set_other_works(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()

    if "photo_links" not in data:
        data["photo_links"] = []

    if message.photo:
        photo_file_id = message.photo[-1].file_id
        data["photo_links"].append(photo_file_id)

    await state.update_data(photo_links=data["photo_links"])

    if len(data["photo_links"]) >= 5:
        await message.answer("⏳Загрузка прикрепленных фото в облако...")
        photo_file_names = await download_photos("Road_clothing", data["photo_links"], message.from_user.id, bot)
        photo_file_names_str = "./media\n".join(photo_file_names)
        await state.update_data(photo_links=photo_file_names_str)

        files_url = []
        for file_name in photo_file_names:
            file_url = await google_disk.upload_file(f"./bot/media/{file_name}")
            files_url.append(file_url)
        files_url_str = "\n".join(files_url)

        await state.update_data(photo_links=files_url_str)

        report_data = await state.get_data()
        await message.answer("✅Фото успешно загружены!")
        await state.set_state(Road_clothing_steps.is_ok)
        await message.answer(f"Отчету по этапу {report_data['stage']}:\n\n"
                        f"Смена: {report_data['shift']}\n"
                        f"Объект: {report_data['project']}\n"
                        f"Подстилающий слой из песка. С какого ПК по какой ПК в формате: 1+00-2+00.: {report_data['underlying_layer']}\n"
                        f"Подстилающий слой из песка. Количество площадь/толщина: {report_data['underlying_layer_area']}\n"
                        f"Дополнительный слой из ПГС. С какого ПК по какой ПК в формате: 1+00-2+00.: {report_data['additional_layer']}\n"
                        f"Дополнительный слой из ПГС. Количество площадь/толщина.: {report_data['additional_layer_area']}\n"
                        f"Устройство основания из щебня. С какого ПК по какой ПК в формате: 1+00-2+00.: {report_data['foundation_construction']}\n"
                        f"Устройство основания из щебня. Количество площадь/толщина.: {report_data['foundation_construction_area']}\n"
                        f"Ссылки на фото:\n{report_data['photo_links']}\n"
                        , reply_markup= await kb.get_report_keyboard())
        
        
@router.message(Road_clothing_steps.is_ok)
async def set_photo_links(message: Message, state: FSMContext):
    await state.update_data(is_ok=message.text)
    if message.text == "Заполнить заново":
        await state.set_state(Road_clothing_steps.underlying_layer)
        await message.answer("Подстилающий слой из песка. Укажите с какого ПК по какой ПК в формате: 1+00-2+00.", reply_markup= await kb.remove_keyboard())
    elif message.text == "Отправить":
        await state.set_state(Material_consumption_report_steps.pgs_quantity)
        await message.answer("ПГС. Укажите количество тонн.", reply_markup=await kb.remove_keyboard())
    else:
        await state.set_state(Road_clothing_steps.is_ok)
        await message.answer("Неизвестная команда", reply_markup=await kb.get_report_keyboard())
        
        
@router.message(Asphalt_steps.cleaning_base)
async def set_photo_links(message: Message, state: FSMContext):
    if re.match(r"(\d+)\+(\d+)-(\d+)\+(\d+)", message.text):
        await state.update_data(cleaning_base=message.text)
        await state.set_state(Asphalt_steps.cleaning_base_area)
        await message.answer("Очистка основания от пыли и грязи механизированным способом. Укажите количество м2.", reply_markup= await kb.remove_keyboard())
    else:
        await state.set_state(Asphalt_steps.cleaning_base)
        await message.answer("Необходимо ввести значение в формате 1+00-2+00!", reply_markup= await kb.remove_keyboard())
    
    
@router.message(Asphalt_steps.cleaning_base_area)
async def set_photo_links(message: Message, state: FSMContext):
    if (message.text).isdigit():
        await state.update_data(cleaning_base_area=message.text)
        await state.set_state(Asphalt_steps.installation_primer)
        await message.answer("Устройство битумной эмульсионной подгрунтовки. Укажите с какого ПК по какой ПК в формате: 1+00-2+00.", reply_markup= await kb.remove_keyboard())
    else:
        await state.set_state(Asphalt_steps.cleaning_base_area)
        await message.answer("Необходимо указать число!", reply_markup= await kb.remove_keyboard()) 
    
    
@router.message(Asphalt_steps.installation_primer)
async def set_photo_links(message: Message, state: FSMContext):
    if re.match(r"(\d+)\+(\d+)-(\d+)\+(\d+)", message.text):
        await state.update_data(installation_primer=message.text)
        await state.set_state(Asphalt_steps.installation_primer_area)
        await message.answer("Устройство битумной эмульсионной подгрунтовки. Укажите количество м2.", reply_markup= await kb.remove_keyboard())
    else:
        await state.set_state(Asphalt_steps.installation_primer)
        await message.answer("Необходимо ввести значение в формате 1+00-2+00!", reply_markup= await kb.remove_keyboard())
         
    
@router.message(Asphalt_steps.installation_primer_area)
async def set_photo_links(message: Message, state: FSMContext):
    if (message.text).isdigit():
        await state.update_data(installation_primer_area=message.text)
        await state.set_state(Asphalt_steps.asphalt_mixture_lower)
        await message.answer("Укладка асфальтобетонной смеси. Нижний слой. Укажите с какого ПК по какой ПК в формате: 1+00-2+00.", reply_markup= await kb.remove_keyboard())
    else:
        await state.set_state(Asphalt_steps.installation_primer_area)
        await message.answer("Необходимо указать число!", reply_markup= await kb.remove_keyboard()) 
        
        
@router.message(Asphalt_steps.asphalt_mixture_lower)
async def set_photo_links(message: Message, state: FSMContext):
    if re.match(r"(\d+)\+(\d+)-(\d+)\+(\d+)", message.text):
        await state.update_data(asphalt_mixture_lower=message.text)
        await state.set_state(Asphalt_steps.asphalt_mixture_lower_area)
        await message.answer("Укладка асфальтобетонной смеси. Нижний слой. Укажите количество площадь/толщина.", reply_markup= await kb.remove_keyboard())
    else:
        await state.set_state(Asphalt_steps.asphalt_mixture_lower)
        await message.answer("Необходимо ввести значение в формате 1+00-2+00!", reply_markup= await kb.remove_keyboard())
    
    
@router.message(Asphalt_steps.asphalt_mixture_lower_area)
async def set_photo_links(message: Message, state: FSMContext):
    if re.match(r"\d+\/\s?\d+", message.text): 
        await state.update_data(asphalt_mixture_lower_area=message.text)
        await state.set_state(Asphalt_steps.asphalt_mixture_upper)
        await message.answer("Укладка асфальтобетонной смеси. Верхний слой. Укажите с какого ПК по какой ПК в формате: 1+00-2+00.", reply_markup= await kb.remove_keyboard())
    else:
        await state.set_state(Asphalt_steps.asphalt_mixture_lower_area)
        await message.answer("Необходимо ввести значение в формате число/число", reply_markup= await kb.remove_keyboard()) 
    
    
@router.message(Asphalt_steps.asphalt_mixture_upper)
async def set_photo_links(message: Message, state: FSMContext):
    if re.match(r"(\d+)\+(\d+)-(\d+)\+(\d+)", message.text):
        await state.update_data(asphalt_mixture_upper=message.text)
        await state.set_state(Asphalt_steps.asphalt_mixture_upper_area)
        await message.answer("Укладка асфальтобетонной смеси. Верхний слой. Укажите количество площадь/толщина.", reply_markup= await kb.remove_keyboard())
    else:
        await state.set_state(Asphalt_steps.asphalt_mixture_upper)
        await message.answer("Необходимо ввести значение в формате 1+00-2+00!", reply_markup= await kb.remove_keyboard())
    
    
@router.message(Asphalt_steps.asphalt_mixture_upper_area)
async def set_photo_links(message: Message, state: FSMContext):
    if re.match(r"\d+\/\s?\d+", message.text): 
        await state.update_data(asphalt_mixture_upper_area=message.text)
        await state.set_state(Asphalt_steps.photo_links)
        await message.answer("Прикрепить 5 четких фото по этому виду работ", reply_markup= await kb.remove_keyboard())
    else:
        await state.set_state(Asphalt_steps.asphalt_mixture_upper_area)
        await message.answer("Необходимо ввести значение в формате число/число", reply_markup= await kb.remove_keyboard()) 
    
    
@router.message(Asphalt_steps.photo_links)
async def set_other_works(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()

    if "photo_links" not in data:
        data["photo_links"] = []

    if message.photo:
        photo_file_id = message.photo[-1].file_id
        data["photo_links"].append(photo_file_id)

    await state.update_data(photo_links=data["photo_links"])

    if len(data["photo_links"]) >= 5:
        await message.answer("⏳Загрузка прикрепленных фото в облако...")
        photo_file_names = await download_photos("Asphalt", data["photo_links"], message.from_user.id, bot)
        photo_file_names_str = "./media\n".join(photo_file_names)
        await state.update_data(photo_links=photo_file_names_str)

        files_url = []
        for file_name in photo_file_names:
            file_url = await google_disk.upload_file(f"./bot/media/{file_name}")
            files_url.append(file_url)
        files_url_str = "\n".join(files_url)

        await state.update_data(photo_links=files_url_str)

        report_data = await state.get_data()
        await message.answer("✅Фото успешно загружены!")
        await state.set_state(Asphalt_steps.is_ok)
        await message.answer(f"Отчету по этапу {report_data['stage']}:\n\n"
                        f"Смена: {report_data['shift']}\n"
                        f"Объект: {report_data['project']}\n"
                        f"Очистка основания от пыли и грязи механизированным способом. С какого ПК по какой ПК в формате: 1+00-2+00: {report_data['cleaning_base']}\n"
                        f"Очистка основания от пыли и грязи механизированным способом. Количество м2: {report_data['cleaning_base_area']}\n"
                        f"Устройство битумной эмульсионной подгрунтовки. С какого ПК по какой ПК в формате: 1+00-2+00: {report_data['installation_primer']}\n"
                        f"Устройство битумной эмульсионной подгрунтовки. Количество м2: {report_data['installation_primer_area']}\n"
                        f"Укладка асфальтобетонной смеси. Нижний слой. С какого ПК по какой ПК в формате: 1+00-2+00: {report_data['asphalt_mixture_lower']}\n"
                        f"Укладка асфальтобетонной смеси. Нижний слой. Количество площадь/толщина: {report_data['asphalt_mixture_lower_area']}\n"
                        f"Укладка асфальтобетонной смеси. Верхний слой. С какого ПК по какой ПК в формате: 1+00-2+00.: {report_data['asphalt_mixture_upper']}\n"
                        f"Укладка асфальтобетонной смеси. Верхний слой. Количество площадь/толщина: {report_data['asphalt_mixture_upper_area']}\n"
                        f"Ссылки на фото:\n{report_data['photo_links']}\n"
                        , reply_markup= await kb.get_report_keyboard())
        
        
@router.message(Asphalt_steps.is_ok)
async def set_photo_links(message: Message, state: FSMContext):
    await state.update_data(is_ok=message.text)
    if message.text == "Заполнить заново":
        await state.set_state(Asphalt_steps.cleaning_base)
        await message.answer("Очистка основания от пыли и грязи механизированным способом. Укажите с какого ПК по какой ПК в формате: 1+00-2+00.", reply_markup= await kb.remove_keyboard())
    elif message.text == "Отправить":
        await state.set_state(Material_consumption_report_steps.pgs_quantity)
        await message.answer("ПГС. Укажите количество тонн.", reply_markup=await kb.remove_keyboard())
    else:
        await state.set_state(Asphalt_steps.is_ok)
        await message.answer("Неизвестная команда", reply_markup=await kb.get_report_keyboard())
        
        
@router.message(Road_devices_steps.characters_number)
async def set_photo_links(message: Message, state: FSMContext):
    if re.match(r"\d+\.\d+\s-\s\d+", message.text): 
        await state.update_data(characters_number=message.text)
        await state.set_state(Road_devices_steps.signal_posts_number)
        await message.answer("Напишите количество сигнальных столбиков, установленных за сегодня.", reply_markup= await kb.remove_keyboard())
    else:
        await state.set_state(Road_devices_steps.characters_number)
        await message.answer("Необходимо ввести значение в формате 3.24-5", reply_markup=await kb.get_report_keyboard())
    
    
@router.message(Road_devices_steps.signal_posts_number)
async def set_photo_links(message: Message, state: FSMContext):
    if (message.text).isdigit():
        await state.update_data(signal_posts_number=message.text)
        await state.set_state(Road_devices_steps.other_works)
        await message.answer("Напишите другую работу с объемом по обстановке дороги.", reply_markup= await kb.remove_keyboard())
    else:
        await state.set_state(Road_devices_steps.signal_posts_number)
        await message.answer("Необходимо указать число!", reply_markup= await kb.remove_keyboard()) 
    
    
@router.message(Road_devices_steps.other_works)
async def set_photo_links(message: Message, state: FSMContext):
    await state.update_data(other_works=message.text)
    await state.set_state(Road_devices_steps.photo_links)
    await message.answer("Прикрепить 5 четких фото по этому виду работ", reply_markup= await kb.remove_keyboard())
    
    
@router.message(Road_devices_steps.photo_links)
async def set_other_works(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()

    if "photo_links" not in data:
        data["photo_links"] = []

    if message.photo:
        photo_file_id = message.photo[-1].file_id
        data["photo_links"].append(photo_file_id)

    await state.update_data(photo_links=data["photo_links"])

    if len(data["photo_links"]) >= 5:
        await message.answer("⏳Загрузка прикрепленных фото в облако...")
        photo_file_names = await download_photos("Asphalt", data["photo_links"], message.from_user.id, bot)
        photo_file_names_str = "./media\n".join(photo_file_names)
        await state.update_data(photo_links=photo_file_names_str)

        files_url = []
        for file_name in photo_file_names:
            file_url = await google_disk.upload_file(f"./bot/media/{file_name}")
            files_url.append(file_url)
        files_url_str = "\n".join(files_url)

        await state.update_data(photo_links=files_url_str)

        report_data = await state.get_data()
        await message.answer("✅Фото успешно загружены!")
        await state.set_state(Road_devices_steps.is_ok)
        await message.answer(f"Отчету по этапу {report_data['stage']}:\n\n"
                        f"Смена: {report_data['shift']}\n"
                        f"Объект: {report_data['project']}\n"
                        f"Нумерация  и количество знаков, установленных за сегодня, в формате 3.24 - 5: {report_data['characters_number']}\n"
                        f"Подстилающий слой из песка. Количество площадь/толщина: {report_data['signal_posts_number']}\n"
                        f"Другая работа с объемом по обстановке дороги: {report_data['other_works']}\n"
                        f"Ссылки на фото:\n{report_data['photo_links']}\n"
                        , reply_markup= await kb.get_report_keyboard())
        
        
@router.message(Road_devices_steps.is_ok)
async def set_photo_links(message: Message, state: FSMContext):
    await state.update_data(is_ok=message.text)
    if message.text == "Заполнить заново":
        await state.set_state(Road_devices_steps.characters_number)
        await message.answer("Напишите нумерацию  и количество знаков, установленных за сегодня, в формате 3.24 - 5", reply_markup= await kb.remove_keyboard())
    elif message.text == "Отправить":
        await state.set_state(Material_consumption_report_steps.pgs_quantity)
        await message.answer("ПГС. Укажите количество тонн.", reply_markup=await kb.remove_keyboard())
    else:
        await state.set_state(Road_devices_steps.is_ok)
        await message.answer("Неизвестная команда", reply_markup=await kb.get_report_keyboard())


@router.message(Material_consumption_report_steps.pgs_quantity)
async def set_photo_links(message: Message, state: FSMContext):
    if (message.text).isdigit():
        await state.update_data(pgs_quantity=message.text)
        await state.set_state(Material_consumption_report_steps.crushed_stone_fraction)
        await message.answer("Щебень. Укажите фракцию щебня.", reply_markup= await kb.remove_keyboard())
    else:
        await state.set_state(Material_consumption_report_steps.pgs_quantity)
        await message.answer("Необходимо указать число!", reply_markup= await kb.remove_keyboard()) 


@router.message(Material_consumption_report_steps.crushed_stone_fraction)
async def set_photo_links(message: Message, state: FSMContext):
    await state.update_data(crushed_stone_fraction=message.text)
    await state.set_state(Material_consumption_report_steps.crushed_stone_quantity)
    await message.answer("Щебень. Укажите количество тонн.", reply_markup= await kb.remove_keyboard())
    

@router.message(Material_consumption_report_steps.crushed_stone_quantity)
async def set_photo_links(message: Message, state: FSMContext):
    if (message.text).isdigit():
        await state.update_data(crushed_stone_quantity=message.text)
        await state.set_state(Material_consumption_report_steps.side_stone)
        await message.answer("Бортовой камень — дорожный или тротуарный?", reply_markup= await kb.remove_keyboard())
    else:
        await state.set_state(Material_consumption_report_steps.crushed_stone_quantity)
        await message.answer("Необходимо указать число!", reply_markup= await kb.remove_keyboard())    
    
    
@router.message(Material_consumption_report_steps.side_stone)
async def set_photo_links(message: Message, state: FSMContext):
    await state.update_data(side_stone=message.text)
    await state.set_state(Material_consumption_report_steps.side_stone_quantity)
    await message.answer("Бортовой камень.  Укажите количество п.м.", reply_markup= await kb.remove_keyboard())
    

@router.message(Material_consumption_report_steps.side_stone_quantity)
async def set_photo_links(message: Message, state: FSMContext):
    if (message.text).isdigit():
        await state.update_data(side_stone_quantity=message.text)
        await state.set_state(Material_consumption_report_steps.ebdc_quantity)
        await message.answer("Эмульсия битумная катионная (ЭБДК (Б)). Укажите количество.", reply_markup= await kb.remove_keyboard())
    else:
        await state.set_state(Material_consumption_report_steps.side_stone_quantity)
        await message.answer("Необходимо указать число!", reply_markup= await kb.remove_keyboard())    
    
@router.message(Material_consumption_report_steps.ebdc_quantity)
async def set_photo_links(message: Message, state: FSMContext):
    if (message.text).isdigit():
        await state.update_data(ebdc_quantity=message.text)
        await state.set_state(Material_consumption_report_steps.asphalt_concrete_mixture)
        await message.answer("Асфальтобетонная смесь. Укажите тип.", reply_markup= await kb.remove_keyboard())
    else:
        await state.set_state(Material_consumption_report_steps.ebdc_quantity)
        await message.answer("Необходимо указать число!", reply_markup= await kb.remove_keyboard())    
    
@router.message(Material_consumption_report_steps.asphalt_concrete_mixture)
async def set_photo_links(message: Message, state: FSMContext):
    await state.update_data(asphalt_concrete_mixture=message.text)
    await state.set_state(Material_consumption_report_steps.asphalt_concrete_scope)
    await message.answer("Асфальтобетонная смесь. Укажите количество м3.", reply_markup= await kb.remove_keyboard())
    
    
@router.message(Material_consumption_report_steps.asphalt_concrete_scope)
async def set_photo_links(message: Message, state: FSMContext):
    if (message.text).isdigit():
        await state.update_data(asphalt_concrete_scope=message.text)
        await state.set_state(Material_consumption_report_steps.concrete_mixture)
        await message.answer("Бетонная смесь. Укажите марку.", reply_markup= await kb.remove_keyboard())
    else:
        await state.set_state(Material_consumption_report_steps.asphalt_concrete_scope)
        await message.answer("Необходимо указать число!", reply_markup= await kb.remove_keyboard())    


@router.message(Material_consumption_report_steps.concrete_mixture)
async def set_photo_links(message: Message, state: FSMContext):
    await state.update_data(concrete_mixture=message.text)
    await state.set_state(Material_consumption_report_steps.concrete_mixture_quantity)
    await message.answer("Бетонная смесь. Укажите количество м3.", reply_markup= await kb.remove_keyboard())
    
    
@router.message(Material_consumption_report_steps.concrete_mixture_quantity)
async def set_photo_links(message: Message, state: FSMContext):
    if (message.text).isdigit():
        await state.update_data(concrete_mixture_quantity=message.text)
        await state.set_state(Material_consumption_report_steps.other_material)
        await message.answer("Другие материалы. Виды и количество?", reply_markup= await kb.remove_keyboard())
    else:
        await state.set_state(Material_consumption_report_steps.concrete_mixture_quantity)
        await message.answer("Необходимо указать число!", reply_markup= await kb.remove_keyboard())    
    
    
@router.message(Material_consumption_report_steps.other_material)
async def set_photo_links(message: Message, state: FSMContext):
    await state.update_data(other_material=message.text)
    await state.set_state(Material_consumption_report_steps.is_ok)
    report_data = await state.get_data()
    await message.answer(f"Отчету по этапу {report_data['stage']}:\n\n"
                f"Смена: {report_data['shift']}\n"
                f"Объект: {report_data['project']}\n"
                f"ПГС. Количество тонн: {report_data['pgs_quantity']}\n"
                f"Щебень. Фракция щебня: {report_data['crushed_stone_fraction']}\n"
                f"Щебень. Количество тонн: {report_data['crushed_stone_quantity']}\n"
                f"Бортовой камень: {report_data['side_stone']}\n"
                f"Бортовой камень. Количество п.м.: {report_data['side_stone_quantity']}\n"
                f"Эмульсия битумная катионная (ЭБДК (Б)). Количество: {report_data['ebdc_quantity']}\n"
                f"Асфальтобетонная смесь. Тип: {report_data['asphalt_concrete_mixture']}\n"
                f"Асфальтобетонная смесь. Количество м3: {report_data['asphalt_concrete_scope']}\n"
                f"Бетонная смесь. Марка: {report_data['concrete_mixture']}\n"
                f"Бетонная смесь. Количество м3: {report_data['concrete_mixture_quantity']}\n"
                f"Другие материалы: {report_data['other_material']}\n"
                , reply_markup= await kb.get_report_keyboard())
      
    
@router.message(Material_consumption_report_steps.is_ok)
async def set_photo_links(message: Message, state: FSMContext):
    await state.update_data(is_ok=message.text)
    if message.text == "Заполнить заново":
        await state.set_state(Material_consumption_report_steps.pgs_quantity)
        await message.answer("ПГС. Укажите количество тонн.", reply_markup=await kb.remove_keyboard())
    elif message.text == "Отправить":
        await state.set_state(People_and_equipment_report_steps.date)
        await message.answer("Напишите дату  в формате (дд.мм.гг)", reply_markup= await kb.remove_keyboard())
    else:
        await state.set_state(Material_consumption_report_steps.is_ok)
        await message.answer("Неизвестная команда", reply_markup=await kb.get_report_keyboard())


@router.message(People_and_equipment_report_steps.date)
async def set_photo_links(message: Message, state: FSMContext):
    if re.match(r"^(0[1-9]|[12][0-9]|3[01])\.(0[1-9]|1[0-2])\.(\d{2})$", message.text): 
        await state.update_data(date=message.text)
        await state.set_state(People_and_equipment_report_steps.people_number)
        await message.answer("Сколько людей на объекте?", reply_markup= await kb.remove_keyboard())
    else:
        await state.set_state(People_and_equipment_report_steps.date)
        await message.answer("Необходимо ввести дату в формате дд.мм.гг!", reply_markup= await kb.remove_keyboard())
       

@router.message(People_and_equipment_report_steps.people_number)
async def set_photo_links(message: Message, state: FSMContext):
    if (message.text).isdigit():
        await state.update_data(people_number=message.text)
        await state.set_state(People_and_equipment_report_steps.equipment_number)
        await message.answer("Сколько техники на объекте?", reply_markup= await kb.remove_keyboard())
    else:
        await state.set_state(People_and_equipment_report_steps.people_number)
        await message.answer("Необходимо указать число!", reply_markup= await kb.remove_keyboard())    
    
    
@router.message(People_and_equipment_report_steps.equipment_number)
async def set_photo_links(message: Message, state: FSMContext):
    if (message.text).isdigit():
        await state.update_data(equipment_number=message.text)
        report_data = await state.get_data()
        await state.set_state(People_and_equipment_report_steps.is_ok)
        await message.answer(f"Отчету по этапу {report_data['stage']}:\n\n"
                            f"Смена: {report_data['shift']}\n"
                            f"Объект: {report_data['project']}\n"
                            f"Этап работ: {report_data['stage']}\n"
                            f"Дата: {report_data['date']}\n"
                            f"Количество людей на объекте: {report_data['people_number']}\n"
                            f"Количество техники на объекте: {report_data['equipment_number']}\n"
                            , reply_markup=await kb.get_report_keyboard())
    else:
        await state.set_state(People_and_equipment_report_steps.equipment_number)
        await message.answer("Необходимо указать число!", reply_markup= await kb.remove_keyboard())   
    
    
@router.message(People_and_equipment_report_steps.is_ok)
async def set_photo_links(message: Message, state: FSMContext):
    await state.update_data(is_ok=message.text)
    if message.text == "Заполнить заново":
        await state.set_state(People_and_equipment_report_steps.date)
        await message.answer("Сколько людей на объекте?", reply_markup= await kb.remove_keyboard())
    elif message.text == "Отправить":
        report_data = await state.get_data()
        if report_data['stage']=="Подготовительные работы":
            await db.add_preparatory_report(
                user_id=message.from_user.id,
                shift=report_data['shift'],
                project=report_data['project'],
                create_datetime=datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
                route_breakdown=report_data['project'],
                clearing_way=report_data['clearing_way'],
                water_disposal=report_data['water_disposal'],
                water_disposal_scope=report_data['water_disposal_scope'],
                removal_utility_networks=report_data['removal_utility_networks'],
                removal_utility_networks_scope=report_data['removal_utility_networks_scope'],
                temporary_construction=report_data['temporary_construction'],
                quarries_construction=report_data['quarries_construction'],
                quarries_construction_quantity=report_data['quarries_construction_quantity'],
                cutting_asphalt_area=report_data['cutting_asphalt_area'],
                other_works=report_data['other_works'],
                photo_links=report_data['photo_links'],
                pgs_quantity=report_data['pgs_quantity'],
                crushed_stone_fraction=report_data['crushed_stone_fraction'],
                crushed_stone_quantity=report_data['crushed_stone_quantity'],
                side_stone=report_data['side_stone'],
                side_stone_quantity=report_data['side_stone_quantity'],
                ebdc_quantity=report_data['ebdc_quantity'],
                asphalt_concrete_mixture=report_data['asphalt_concrete_mixture'],
                asphalt_concrete_scope=report_data['asphalt_concrete_scope'],
                concrete_mixture=report_data['concrete_mixture'],
                concrete_mixture_quantity=report_data['concrete_mixture_quantity'],
                other_material=report_data['other_material'],
                date=datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
                people_number=report_data['people_number'],
                equipment_number=report_data['equipment_number']
                )
        elif report_data['stage']=="Земляные работы":
            await db.add_earthworks_report(
                user_id=message.from_user.id,
                shift=report_data['shift'],
                project=report_data['project'],
                create_datetime=datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
                detailed_breakdown=report_data['detailed_breakdown'],
                excavations_development=report_data['excavations_development'],
                excavations_development_quantity=report_data['excavations_development_quantity'],
                soil_compaction=report_data['soil_compaction'],
                soil_compaction_quantity=report_data['soil_compaction_quantity'],
                final_layout=report_data['final_layout'],
                final_layout_quantity=report_data['final_layout_quantity'],
                photo_links=report_data['photo_links'],
                pgs_quantity=report_data['pgs_quantity'],
                crushed_stone_fraction=report_data['crushed_stone_fraction'],
                crushed_stone_quantity=report_data['crushed_stone_quantity'],
                side_stone=report_data['side_stone'],
                side_stone_quantity=report_data['side_stone_quantity'],
                ebdc_quantity=report_data['ebdc_quantity'],
                asphalt_concrete_mixture=report_data['asphalt_concrete_mixture'],
                asphalt_concrete_scope=report_data['asphalt_concrete_scope'],
                concrete_mixture=report_data['concrete_mixture'],
                concrete_mixture_quantity=report_data['concrete_mixture_quantity'],
                other_material=report_data['other_material'],
                date=datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
                people_number=report_data['people_number'],
                equipment_number=report_data['equipment_number']
            )
        elif report_data['stage']=="Искусственные сооружения":
            await db.add_artificial_structures_report(
                user_id=message.from_user.id,
                shift=report_data['shift'],
                project=report_data['project'],
                create_datetime=datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
                work_type=report_data['work_type'],
                work_scope=report_data['work_scope'],
                photo_links=report_data['photo_links'],
                pgs_quantity=report_data['pgs_quantity'],
                crushed_stone_fraction=report_data['crushed_stone_fraction'],
                crushed_stone_quantity=report_data['crushed_stone_quantity'],
                side_stone=report_data['side_stone'],
                side_stone_quantity=report_data['side_stone_quantity'],
                ebdc_quantity=report_data['ebdc_quantity'],
                asphalt_concrete_mixture=report_data['asphalt_concrete_mixture'],
                asphalt_concrete_scope=report_data['asphalt_concrete_scope'],
                concrete_mixture=report_data['concrete_mixture'],
                concrete_mixture_quantity=report_data['concrete_mixture_quantity'],
                other_material=report_data['other_material'],
                date=datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
                people_number=report_data['people_number'],
                equipment_number=report_data['equipment_number']
            )
        elif report_data['stage']=="Дорожная одежда":
            await db.add_road_clothing_report(
                user_id=message.from_user.id,
                shift=report_data['shift'],
                project=report_data['project'],
                create_datetime=datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
                underlying_layer=report_data['underlying_layer'],
                underlying_layer_area=report_data['underlying_layer_area'],
                additional_layer=report_data['additional_layer'],
                additional_layer_area=report_data['additional_layer_area'],
                foundation_construction=report_data['foundation_construction'],
                foundation_construction_area=report_data['foundation_construction_area'],
                photo_links=report_data['photo_links'],
                pgs_quantity=report_data['pgs_quantity'],
                crushed_stone_fraction=report_data['crushed_stone_fraction'],
                crushed_stone_quantity=report_data['crushed_stone_quantity'],
                side_stone=report_data['side_stone'],
                side_stone_quantity=report_data['side_stone_quantity'],
                ebdc_quantity=report_data['ebdc_quantity'],
                asphalt_concrete_mixture=report_data['asphalt_concrete_mixture'],
                asphalt_concrete_scope=report_data['asphalt_concrete_scope'],
                concrete_mixture=report_data['concrete_mixture'],
                concrete_mixture_quantity=report_data['concrete_mixture_quantity'],
                other_material=report_data['other_material'],
                date=datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
                people_number=report_data['people_number'],
                equipment_number=report_data['equipment_number']
            )
        elif report_data['stage']=="Асфальт":
            await db.add_asphalt_clothing_report(
                user_id=message.from_user.id,
                shift=report_data['shift'],
                project=report_data['project'],
                create_datetime=datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
                cleaning_base=report_data['cleaning_base'],
                cleaning_base_area=report_data['cleaning_base_area'],
                installation_primer=report_data['installation_primer'],
                installation_primer_area=report_data['installation_primer_area'],
                asphalt_mixture_lower=report_data['asphalt_mixture_lower'],
                asphalt_mixture_lower_area=report_data['asphalt_mixture_lower_area'],
                asphalt_mixture_upper=report_data['asphalt_mixture_upper'],
                asphalt_mixture_upper_area=report_data['asphalt_mixture_upper_area'],
                photo_links=report_data['photo_links'],
                pgs_quantity=report_data['pgs_quantity'],
                crushed_stone_fraction=report_data['crushed_stone_fraction'],
                crushed_stone_quantity=report_data['crushed_stone_quantity'],
                side_stone=report_data['side_stone'],
                side_stone_quantity=report_data['side_stone_quantity'],
                ebdc_quantity=report_data['ebdc_quantity'],
                asphalt_concrete_mixture=report_data['asphalt_concrete_mixture'],
                asphalt_concrete_scope=report_data['asphalt_concrete_scope'],
                concrete_mixture=report_data['concrete_mixture'],
                concrete_mixture_quantity=report_data['concrete_mixture_quantity'],
                other_material=report_data['other_material'],
                date=datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
                people_number=report_data['people_number'],
                equipment_number=report_data['equipment_number']                
            )
        elif report_data['stage']=="Дорожные устройства и обстановка дороги":
            await db.add_road_devices_report(
                user_id=message.from_user.id,
                shift=report_data['shift'],
                project=report_data['project'],
                create_datetime=datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
                characters_number=report_data['characters_number'],
                signal_posts_number=report_data['signal_posts_number'],
                other_works=report_data['other_works'],
                photo_links=report_data['photo_links'],
                pgs_quantity=report_data['pgs_quantity'],
                crushed_stone_fraction=report_data['crushed_stone_fraction'],
                crushed_stone_quantity=report_data['crushed_stone_quantity'],
                side_stone=report_data['side_stone'],
                side_stone_quantity=report_data['side_stone_quantity'],
                ebdc_quantity=report_data['ebdc_quantity'],
                asphalt_concrete_mixture=report_data['asphalt_concrete_mixture'],
                asphalt_concrete_scope=report_data['asphalt_concrete_scope'],
                concrete_mixture=report_data['concrete_mixture'],
                concrete_mixture_quantity=report_data['concrete_mixture_quantity'],
                other_material=report_data['other_material'],
                date=datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
                people_number=report_data['people_number'],
                equipment_number=report_data['equipment_number']    
            )

        user_fullname = await db.get_fullname(message.from_user.id)
        await google_disk.upload_report(report_data, user_fullname)
        for id in Config.ADMIN_IDS:
            await message.bot.send_message(id, f"{user_fullname} отправил отчет")
        await state.clear()
        await message.answer("Поздравляем! Все отчеты приняты!", reply_markup= await kb.get_main_menu_keyboard())
    else:
        await state.set_state(Material_consumption_report_steps.is_ok)
        await message.answer("Неизвестная команда", reply_markup=await kb.get_report_keyboard())


@router.callback_query(F.data)
async def track_callback(callback: CallbackQuery, bot: Bot):
    pass


async def download_photos(report_name, photo_file_ids, user_id, bot):
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M")
    photo_file_names = []

    if not os.path.exists("./bot/media"):
        os.makedirs("./bot/media")

    for i, photo_file_id in enumerate(photo_file_ids):
        file_name = f"{report_name}_{user_id}_{current_time}_{i + 1}.jpg"
        file_path = os.path.join("./bot/media", file_name)

        try:
            file = await bot.get_file(photo_file_id)
            await bot.download_file(file.file_path, destination=file_path)
            photo_file_names.append(file_name)
        except Exception as error:
            print(f"Ошибка при скачивании фотографии {file_name}: {error}")

    return photo_file_names


async def send_morning_notification(bot):
    try:
        user_ids = await db.get_all_user_id()
        for user_id in user_ids:
            await bot.send_message(user_id, 'Добрый день. Время заполнять отчет для ночной смены. Нажмите "Старт".')
    except Exception as error:
        print(f"Ошибка при отправке утреннего напоминания: {error}")
        

async def send_evening_notification(bot):
    print("Напоминалка")
    try:
        user_ids = await db.get_all_user_id()
        for user_id in user_ids:
            await bot.send_message(user_id,  'Добрый день. Время заполнять отчет для дневной смены. Нажмите "Старт".')
    except Exception as error:
        print(f"Ошибка при отправке вечернего напоминания: {error}")