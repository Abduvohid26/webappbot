from aiogram.fsm.context import FSMContext
from loader import dp, db
from aiogram import types, F, html
from data.config import OPENAI_KEY, BOT_TOKEN, BOT_USERNAME
from openai import OpenAI
from loader import bot
from aiogram.enums.chat_action import ChatAction
from states.my_state import Image_Analyze
from filters.my_filter import MyFilter
from handlers.channels.fetch_count import is_fetch_limit_reached
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types.web_app_info import WebAppInfo
from data.config import MINI_APP_URL
import asyncio
from handlers.webapp.app import random_webapp_url
from keyboards.default.button import menu_button
from aiogram.utils.i18n import gettext as _
import base64





@dp.callback_query(F.data == "referal_premium")
async def start_premium(call: types.CallbackQuery):
    await call.answer(cache_time=60)
    btn = InlineKeyboardBuilder()
    tariff_options = db.select__all_tarif()
    if not tariff_options:
        btn.button(text=_("back_to_main_menu"), callback_data="main_menu_back")
        await call.message.answer(text="Tariflar mavjud emas admin bilan bog'laning \n📞 Admin: @Jovohuz", reply_markup=btn.as_markup())
        return
    for tarif in tariff_options:
        btn.button(text=f"{tarif[2]} - {tarif[1]} ta", callback_data=f"tariff_{tarif[1]}_{tarif[2]}")
    btn.button(text=_("back_to_main_menu"), callback_data="main_menu_back")
    btn.adjust(1)
    await call.message.answer("Quyidagi tariflardan birini tanlang:\n\n♻️ Mos tarifni tanlab sotib olishingiz mumkin", reply_markup=btn.as_markup())


@dp.callback_query(F.data.startswith("tariff_"))
async def get_tariff(call: types.CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    data = call.data.split("_")
    amount = (data[1])
    price = (data[2])
    message_text = (
        f"✅ *Siz {amount} dona xizmatni tanladingiz!*\n\n"
        f"💰 *Narx:* {price}$\n"
        f"📌 Ushbu tarifdan foydalanish uchun admin bilan bog‘laning.\n\n"
        f"📞 *Admin: @Jovohuz*"
    )
    btn = InlineKeyboardBuilder()
    btn.button(text=_("back_to_main_menu"), callback_data="main_menu_back")
    await call.message.answer(text=message_text, parse_mode="Markdown", reply_markup=btn.as_markup())
