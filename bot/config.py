import json
import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Загрузка переменных окружения
if os.path.exists(os.path.join(BASE_DIR, '.env.local')):
    load_dotenv(os.path.join(BASE_DIR, '.env.local'))
else:
    load_dotenv(os.path.join(BASE_DIR, '.env'))


class Config:
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
    DB_URL=os.getenv('DB_URL')
    ADMIN_IDS = json.loads(os.getenv('ADMIN_IDS', '[]'))
    GOOGLE_CREDENTIALS_PATH = os.getenv('GOOGLE_CREDENTIALS_PATH')
    GOOGLE_SCOPES = json.loads(os.getenv('GOOGLE_SCOPES', '[]'))
    GOOGLE_MEDIA_FOLDER_ID = os.getenv('GOOGLE_MEDIA_FOLDER_ID')
    GOOGLE_REPORTS_FILE_ID = os.getenv('GOOGLE_REPORTS_FILE_ID')
    GOOGLE_DIRECTORY_ID = os.getenv('GOOGLE_DIRECTORY_ID')