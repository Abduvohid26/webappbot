from aiogram.filters import CommandStart
from loader import dp, db, BASE_DIR
from aiogram import types, F, html
from data.config import OPENAI_KEY, BOT_TOKEN, MINI_APP_URL
from openai import OpenAI, RateLimitError
import asyncio
from loader import bot
from aiogram.enums.chat_action import ChatAction
from keyboards.default.button import menu_button
from filters.my_filter import MyFilter
from middlewares.my_middleware import CheckSubCallback
from utils.misc.subscription import checksubscription
from handlers.channels.fetch_count import is_fetch_limit_reached
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types.web_app_info import WebAppInfo
from handlers.webapp.app import random_webapp_url
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _



@dp.callback_query(F.data == "change_language_main")
async def change_lang(call: types.CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    btn = InlineKeyboardBuilder()
    btn.button(text="🇺🇿 Uzbek", callback_data="change_lang_uz")
    btn.button(text="🇷🇺 Русский", callback_data="change_lang_ru")
    btn.button(text="🇬🇧 English", callback_data="change_lang_en")
    btn.button(text=_("back_to_main_menu"), callback_data="main_menu_lang_back")
    btn.adjust(1)
    await call.message.answer(text=_("change_lang"), reply_markup=btn.as_markup())



@dp.callback_query(F.data == "main_menu_lang_back")
async def back_button(call: types.CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    await state.clear()
    await call.message.answer(text=_("back_to_main_menu"), reply_markup=menu_button())

@dp.callback_query(F.data.startswith('change_lang_'))
async def get_and_save_lang(call: types.CallbackQuery):
    await call.answer(cache_time=60)
    lang = call.data.split('_')[-1]
    print(lang)
    try:
        db.update_user_lang(telegram_id=call.message.chat.id, lang_code=lang)
        await call.message.answer(text=_("language_changed"))
        return
    except Exception as e:
        print(f"Xatolik Yuz berdi: {e}")
        await call.message.answer(f"Xatolik Yuz berdi: {e}")
