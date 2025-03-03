from aiogram.fsm.state import StatesGroup, State


#Регистрация
class Register_steps(StatesGroup):
    fullname = State() #ФИО


#Выбор смены и этапа работ
class Construction_projects_steps(StatesGroup):
    shift = State() #смена
    stage = State() #этап работ
    project = State() #Объект


#Отчет по этапу "Подготовительные работы"
class Preparatory_steps(Construction_projects_steps):
    route_breakdown = State() #Разбивка трассы. Укажите количество км.
    clearing_way = State() #Расчистка полосы отвода. Укажите количество км.
    water_disposal = State() #Водоотведение и временное водопонижение. Укажите вид работ.
    water_disposal_scope = State() #Водоотведение и временное водопонижение. Укажите объем работ.
    removal_utility_networks = State() #Вынос инженерных сетей и снос зданий и сооружений. Укажите вид работ.
    removal_utility_networks_scope = State() #Вынос инженерных сетей и снос зданий и сооружений. Укажите объем работ.
    temporary_construction = State() #Устройство временных автодорог и объездов. Укажите количество км.
    quarries_construction = State() #Устройство карьеров и резервов. Укажите какой материал привезли?
    quarries_construction_quantity = State() #Устройство карьеров и резервов. Укажите количество в тоннах.
    cutting_asphalt_area = State() #Срезка асфальтобетонного покрытия методом холодного фрезерования. Укажите площадь в м².
    other_works = State() #Другие работы? Опишите.
    photo_links = State() #Ссылки на фото.
    is_ok = State()


#Отчет по этапу "Земляные работы"
class Earthworks_steps(Construction_projects_steps):
    detailed_breakdown = State() #Детальная разбивка элементов дороги и подготовка основания Укажите с какого ПК по какой ПК в формате: 1+00-2+00
    excavations_development = State() #Разработка выемок и возведение насыпей. Укажите вид работ.
    excavations_development_quantity = State() #Разработка выемок и возведение насыпей. Укажите количество в м3.
    soil_compaction = State() #Уплотнение грунта. Укажите с какого ПК по какой ПК в формате: 1+00-2+00
    soil_compaction_quantity = State() #Уплотнение грунта. Укажите количество в м3.
    final_layout = State() #Окончательная планировка.  Укажите с какого ПК по какой ПК в формате: 1+00-2+00
    final_layout_quantity = State() #Окончательная планировка. Укажите количество в м2.
    photo_links = State() #Ссылки на фото.
    is_ok = State()


#Отчет по этапу "Искусственные сооружения"
class Artificial_structures_steps(Construction_projects_steps):
    work_type = State() #Укажите вид работ.
    work_scope = State() #Укажите объем работ.
    photo_links = State() #Ссылки на фото.
    is_ok = State()


#Отчет по этапу "Дорожная одежда"
class Road_clothing_steps(Construction_projects_steps):
    underlying_layer = State() #Подстилающий слой из песка. Укажите с какого ПК по какой ПК в формате: 1+00-2+00.
    underlying_layer_area = State() #Подстилающий слой из песка. Укажите количество площадь/толщина.
    additional_layer = State() #Дополнительный слой из ПГС. Укажите с какого ПК по какой ПК в формате: 1+00-2+00.
    additional_layer_area = State() #Дополнительный слой из ПГС. Укажите количество площадь/толщина.
    foundation_construction = State() #Устройство основания из щебня. Укажите с какого ПК по какой ПК в формате: 1+00-2+00.
    foundation_construction_area = State() #Устройство основания из щебня. Укажите количество площадь/толщина.
    photo_links = State() #Ссылки на фото.
    is_ok = State()


#Отчет по этапу "Асфальт"
class Asphalt_steps(Construction_projects_steps):
    cleaning_base = State() #Очистка основания от пыли и грязи механизированным способом. Укажите с какого ПК по какой ПК в формате: 1+00-2+00.
    cleaning_base_area = State()  #Очистка основания от пыли и грязи механизированным способом. Укажите количество м2.
    installation_primer = State() #Устройство битумной эмульсионной подгрунтовки. Укажите с какого ПК по какой ПК в формате: 1+00-2+00.
    installation_primer_area = State() #Устройство битумной эмульсионной подгрунтовки. Укажите количество м2.
    asphalt_mixture_lower  = State() #Укладка асфальтобетонной смеси. Нижний слой. Укажите с какого ПК по какой ПК в формате: 1+00-2+00.
    asphalt_mixture_lower_area = State() #Укладка асфальтобетонной смеси. Нижний слой. Укажите количество площадь/толщина.
    asphalt_mixture_upper  = State() #Укладка асфальтобетонной смеси. Верхний слой. Укажите с какого ПК по какой ПК в формате: 1+00-2+00.
    asphalt_mixture_upper_area = State() #Укладка асфальтобетонной смеси. Верхний слой. Укажите количество площадь/толщина.
    photo_links = State() #Ссылки на фото.
    is_ok = State()


#Отчет по этапу "Дорожные устройства и обстановка дороги"
class Road_devices_steps(Construction_projects_steps):
    characters_number = State() #Напишите нумерацию  и количество знаков, установленных за сегодня, в формате 3.24 - 5
    signal_posts_number = State() #Напишите количество сигнальных столбиков, установленных за сегодня.
    other_works = State() #Напишите другую работу с объемом по обстановке дороги, например:  "установка барьерного ограждения."
    photo_links = State() #Ссылки на фото.
    is_ok = State()

#Отчет по расходу материала на объекте
class Material_consumption_report_steps(Construction_projects_steps):
    pgs_quantity = State() #ПГС. Укажите количество тонн.
    crushed_stone_fraction = State() #Щебень. Укажите фракцию щебня.
    crushed_stone_quantity = State() #Щебень. Укажите количество тонн.
    side_stone = State() #Бортовой камень — дорожный или тротуарный? 
    side_stone_quantity = State() #Бортовой камень.  Укажите количество п.м.
    ebdc_quantity = State() #Эмульсия битумная катионная (ЭБДК (Б)). Укажите количество. 
    asphalt_concrete_mixture = State() #Асфальтобетонная смесь. Укажите тип.
    asphalt_concrete_scope = State() #Асфальтобетонная смесь. Укажите количество м3. 
    concrete_mixture = State() #Бетонная смесь. Укажите марку.
    concrete_mixture_quantity = State() #Бетонная смесь. Укажите количество м3.
    other_material = State() #Другие материалы. Виды и количество?
    is_ok = State()


#Отчет по количеству людей и техники на объекте
class People_and_equipment_report_steps(Material_consumption_report_steps):
    date = State() #Напишите дату  в формате. дд.мм.гг
    people_number = State() #Сколько людей на объекте?
    equipment_number = State() #Сколько техники на объекте?
    is_ok = State()

