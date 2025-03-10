import os
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.http import MediaFileUpload
from bot.config import Config
import pandas as pd
from bot.database.db import update_all_user_status, update_construction_project, mark_report_as_uploaded, get_not_uploaded_reports
from datetime import datetime
import httplib2
from asyncio import sleep

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

        return file_url
    except Exception as error:
        print(f"Ошибка при загрузке файла: {error}")


async def delete_local_file(file_path):
    try:
        os.remove(file_path)
    except Exception as error:
        print(f"Ошибка при удалении локального файла {file_path}: {error}")


async def upload_stage_report(reports_data, user_fullname):
    try:
        sheet_name = reports_data.get("stage", "")

        user_data = {
            "report_date": str(datetime.now().strftime("%d.%m.%Y")),
            "project": reports_data.get("project", ""),
            "fullname": user_fullname,
            "shift": reports_data.get("shift", ""),
        }

        # Удаляем ненужные ключи из reports_data
        keys_to_remove = ["shift", "project", "stage", "is_ok", "report" ]
        for key in keys_to_remove:
            reports_data.pop(key, None)

        values = {**user_data, **reports_data}
        range_name = f"{sheet_name}!A:Z"

        for key in values:
            if values[key] == "":
                values[key] == "-"

        body = {
            'values': [list(values.values())]
        }

        sheets_service.spreadsheets().values().append(
            spreadsheetId=Config.GOOGLE_REPORTS_FILE_ID,
            range=range_name,
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()

        await mark_report_as_uploaded(user_data.get("stage", ""), user_data.get("report_date", ""))

    except Exception as error:
        print(f"Ошибка при добавлении данных в Google Таблицу: {error}")


async def upload_people_and_equipment_report(report_data, user_fullname):
    try:
        user_data = {
            "report_date": str(datetime.now().strftime("%d.%m.%Y")),
            "project": report_data.get("project", ""),
            "fullname": user_fullname,
            "shift": report_data.get("shift", ""),
        }

        sheet_name = "Отчёт по количеству людей и техники на объекте"
        range_name = f"{sheet_name}!A:Z"

        # Удаляем ненужные ключи из report_data
        keys_to_remove = ["is_ok"]
        for key in keys_to_remove:
            report_data.pop(key, None)

        values = {**user_data, **report_data}

        for key in values:
            if values[key] == "":
                values[key] == "-"
        
        body = {
                'values': [list(values.values())]
            }

        sheets_service.spreadsheets().values().append(
            spreadsheetId=Config.GOOGLE_REPORTS_FILE_ID,
            range=range_name,
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()

        await mark_report_as_uploaded(sheet_name, report_data.get("report_date", ""))
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
    try:
        not_uploaded_reports = await get_not_uploaded_reports()
        if not not_uploaded_reports:
            return
        for report in not_uploaded_reports:
            if report['report_name'] == 'people_and_equipment_reports':
                await upload_people_and_equipment_report(report["report_data"], "БД")
            else:
                await upload_stage_report(report["report_data"], "БД")
    except Exception as error:
        print(f"Ошибка при выгрузке невыгруженнвх отчётов: {error}")