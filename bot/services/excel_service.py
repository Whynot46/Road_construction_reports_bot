from datetime import datetime
from typing import Optional

from bot.database.repositories.my_table import MyTableepository
from bot.helpers.file_logger import log_system_event, LogTypesEnum
from bot.services.yandex_disk_service import YandexDiskService
import pandas as pd
from bot.helpers.messages import Messages as MSG

class ExcelService:
    def __init__(self):
        self.yandex_service = YandexDiskService()

    async def get_yandex_table_data(self, sheet_name: Optional[str] = None):
        """Скачивает файл с Яндекс.Диска и обрабатывает данные."""
        result = ""
        try:
            file_content = await self.yandex_service.download_file()
            result = await self.process_excel_file(file_content, sheet_name)
        finally:
            # Удаляем временный файл после обработки
            self.yandex_service.delete_temp_file()
        return result

    async def process_excel_file(self, file_content, sheet_name_for_sync: Optional[str] = None):
        """
        Читает Excel-файл и добавляет новые записи в соответствующие таблицы.
        """
        if not file_content:
            log_system_event(LogTypesEnum.ERROR.value, "Ошибка чтения файла с Яндекс.Диска")
            return

        # Загружаем содержимое файла в pandas
        # Читаем все листы (sheet_name = None, либо переданный sheet_name = Какое-то имя), указываем, что все поля
        # читать как строки
        excel_data = pd.read_excel(file_content, sheet_name=None, dtype=str)
        result = ""
        result_text = ""

        for sheet_name, data in excel_data.items():
            result = await self.sync_data_page_one(data)
            log_system_event(LogTypesEnum.INFO.value, f"Загружены данные с листа: {sheet_name}")

            result_text += f"{sheet_name}: {result}\n"
        return result_text

    async def sync_data_page_one(self, data):
        """Синхронизирует данные."""
        try:
            async with MyTableepository() as repository:
            # удаляем все из таблицы, если нужно
                await repository.clear_table()
                models = []
                for _, row in data.iterrows():
                    #Добавляем новую запись
                    kwargs = {
                        "id": row.get(0),
                        "name": row.get(1),
                    }
                    new_model = repository.load(**kwargs)
                    if new_model:
                        models.append(new_model)
                models = await repository.create_all(models)
                if not models:
                    raise ValueError(MSG.ERROR_SAVE_DATA_FROM_SHEET)
                return 'Ok'
        except Exception as e:
            log_system_event(LogTypesEnum.ERROR.value, f"Error processing sheet: {e}")
            c = MSG.ERROR_SAVE_DATA_FROM_SHEET.format(error=e)
            log_system_event(LogTypesEnum.ERROR.value, c)
            return c

# Функция для конвертации строки в datetime или None
def parse_date(date_str):
    if pd.notna(date_str):  # Проверяем, не является ли значение NaN
        try:
            # Попытка преобразовать строку в объект datetime
            return pd.to_datetime(date_str).to_pydatetime()
        except ValueError:
            # Если формат даты некорректный, возвращаем None
            return None
    return None
