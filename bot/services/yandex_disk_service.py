import asyncio
import yadisk
import pandas as pd
from io import BytesIO
from os import remove, path
from bot.config import Config


yadisk_client = yadisk.YaDisk(token=Config.YANDEX_DISK_TOKEN)
# yadisk_client = yadisk.YaDisk(token="y0__xCFqb37BxijzTUg0au0shInwu3lP71gj2pj3MZzhSV--NklNQ")


async def download_file(file_path):
    try:
        file_data = BytesIO()
        yadisk_client.download(file_path, file_data)
        file_data.seek(0) 
        return file_data
    except yadisk.exceptions.PathNotFoundError:
        print(f"Файл {file_path} не найден на Яндекс.Диске.")
        return None
    except Exception as e:
        print(f"Ошибка при загрузке файла {file_path}: {e}")
        return None
    
    
async def delete_local_file(file_name):
    try:
        remove(f"./media/{file_name}")
    except Exception as e:
        print(f"Ошибка при удалении файла {file_name}: {e}")


async def update_users():
    file_path = "/Онлайн таблица руководителя.xlsx"
    file_data = await download_file(file_path)
    try:
        with pd.ExcelFile(file_data) as excel:
            df_employees = pd.read_excel(excel, sheet_name="СОТРУДНИКИ")
            employees_data = df_employees.to_dict(orient="records")

            return employees_data

    except Exception as e:
        print(f"Ошибка при чтении Excel-файла: {e}")
        return None


async def update_projects():
    file_path = "/Онлайн таблица руководителя.xlsx"
    file_data = await download_file(file_path)
    try:
        with pd.ExcelFile(file_data) as excel:
            df_projects = pd.read_excel(excel, sheet_name="ОБЪЕКТЫ")
            projects_data = df_projects.to_dict(orient="records")

            return projects_data

    except Exception as e:
        print(f"Ошибка при чтении {file_path}: {e}")
        return None
    

async def upload_file(file_name):
    local_file_path = f"bot/media/{file_name}"
    remote_file_path = f"/media/{file_name}"

    try:
        if not path.exists(local_file_path):
            print(f"Файл {local_file_path} не найден локально.")
        yadisk_client.upload(local_file_path, remote_file_path)
        yadisk_client.publish(remote_file_path)
        file_info = yadisk_client.get_meta(remote_file_path)
        public_url = file_info.public_url
        remove(local_file_path)

        return public_url

    except yadisk.exceptions.PathNotFoundError:
        print(f"Указанный путь на Яндекс.Диске не найден: {remote_file_path}")
    except yadisk.exceptions.ForbiddenError:
        print(f"Нет доступа для загрузки файла на Яндекс.Диск: {remote_file_path}")
    except Exception as e:
        print(f"Ошибка при загрузке файла {file_name} на Яндекс.Диск: {e}")
        