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
    YANDEX_DISK_TOKEN = os.getenv('YANDEX_DISK_TOKEN')
    YANDEX_DISK_FILE_PATH = os.getenv('YANDEX_DISK_FILE_PATH')
    LOG_ROTATE_DAYS = int(os.getenv('LOG_ROTATE_DAYS', 15))

