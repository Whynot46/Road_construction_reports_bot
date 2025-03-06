import os
import aiofiles
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.http import MediaFileUpload
from bot.config import Config
import pandas as pd
from bot.database.db import update_all_user_status, update_construction_project, mark_report_as_uploaded, get_not_uploaded_reports
from datetime import datetime
import httplib2


# Аутентификация через Service Account
creds_service = ServiceAccountCredentials.from_json_keyfile_name(Config.GOOGLE_CREDENTIALS_PATH, scopes=Config.GOOGLE_SCOPES).authorize(httplib2.Http())
# Создание сервисов для работы с Google Drive и Google Sheets
drive_service = build('drive', 'v3', http=creds_service)
sheets_service = build('sheets', 'v4', http=creds_service)


async def upload_file(file_path, folder_id=Config.GOOGLE_MEDIA_FOLDER_ID):
    try:
        file_metadata = {
            'name': os.path.basename(file_path),
            'parents': [folder_id] if folder_id else []
        }
        media = MediaFileUpload(file_path, resumable=True)
        file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()

        file_id = file.get('id')
        file_url = f"https://drive.google.com/file/d/{file_id}/view"
        
        await delete_file(file_path)

        return file_url
    except Exception as error:
        print(f"Ошибка при загрузке файла: {error}")


async def delete_file(file_path):
    try:
        async with aiofiles.open(file_path, 'rb') as file:
            pass  # Файл автоматически закроется после выхода из блока with
        os.remove(file_path)
    except Exception as error:
        print(f"Ошибка при удалении файла: {error}")


async def upload_report(reports_data, user_fullname):
    try:
        sheet_name = reports_data.get("stage", "")

        user_data = {
            "report_date": str(datetime.now().strftime("%Y-%m-%d")),
            "project": reports_data.get("project", ""),
            "fullname": user_fullname,
            "shift": reports_data.get("shift", ""),
        }

        people_and_equipment_report = {
            "date": reports_data.get("date", ""),
            "people_number":  reports_data["people_number"],
            "equipment_number": reports_data["equipment_number"]
        }

        # Удаляем ненужные ключи из reports_data
        keys_to_remove = ["shift", "project", "stage", "is_ok", "people_number", "equipment_number"]
        for key in keys_to_remove:
            reports_data.pop(key, None)

        values = {**user_data, **reports_data, **people_and_equipment_report}
        range_name = f"{sheet_name}!A:Z"

        body = {
            'values': [list(values.values())]
        }

        sheets_service.spreadsheets().values().append(
            spreadsheetId=Config.GOOGLE_REPORTS_FILE_ID,
            range=range_name,
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()

        await mark_report_as_uploaded(user_data.get("stage", ""), user_data.get("report_data", ""))

    except Exception as error:
        print(f"Ошибка при добавлении данных в Google Таблицу: {error}")


async def update_users():
    try:
        sheet_name = "СОТРУДНИКИ"
        range_name = f"{sheet_name}!A:Z"
        result = sheets_service.spreadsheets().values().get(
            spreadsheetId=Config.GOOGLE_DIRECTORY_ID,
            range=range_name
        ).execute()
        
        values = result.get('values', [])
        if not values:
            return
        
        df_employees = pd.DataFrame(values[1:], columns=values[0])
        employees_data = df_employees.to_dict(orient="records")
        
        await update_all_user_status(employees_data)

    except Exception as error:
        print(f"Ошибка при чтении Google Таблицы: {error}")


async def update_projects():
    try:
        sheet_name = "ОБЪЕКТЫ"
        range_name = f"{sheet_name}!A:Z"
        result = sheets_service.spreadsheets().values().get(
            spreadsheetId=Config.GOOGLE_DIRECTORY_ID,
            range=range_name
        ).execute()
        
        values = result.get('values', [])
        if not values:
            return
        
        df_projects = pd.DataFrame(values[1:], columns=values[0])
        projects_data = df_projects.to_dict(orient="records")
        
        await update_construction_project(projects_data)

    except Exception as error:
        print(f"Ошибка при чтении Google Таблицы: {error}")


async def upload_not_uploaded_reports():
    pass
