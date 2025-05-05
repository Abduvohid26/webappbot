from pathlib import Path
from aiogram import Bot, Dispatcher
from data.config import BOT_TOKEN
from utils.db_api.sqlite import Database
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums.parse_mode import ParseMode
from aiogram.client.default import DefaultBotProperties
import gettext
import os
from aiogram.utils.i18n import I18n

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())
BASE_DIR = Path(__file__).resolve().parent
db = Database(path_to_db='data/main.db')
i18n = I18n(path="locales", default_locale="uz", domain="messages")
