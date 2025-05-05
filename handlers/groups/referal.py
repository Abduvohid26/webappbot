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


@dp.callback_query(F.data == "main_menu_back_referal")
async def back_button(call: types.CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    await state.clear()
    await call.message.answer(text=_("main_menu"), reply_markup=menu_button())

def referal_button():
    btn = InlineKeyboardBuilder()
    btn.button(text="👥 Dost taklif qilish", callback_data="referal_offer")
    btn.button(text=_("Premuium tarif"), callback_data="referal_premium")
    btn.button(text=_("back_to_main_menu"), callback_data="main_menu_back_referal")
    btn.adjust(1)
    return btn.as_markup()

@dp.callback_query(F.data == "referals")
async def referals(call: types.CallbackQuery):
    await call.answer(cache_time=60)
    data = db.select_referal_by_user_id(user_id=call.message.chat.id)
    offer_count = db.get_user_fetch_count(user_id=call.message.chat.id)
    reklama_count = db.select_all_reklama()[0][1]
    taklif_qilganlar = data[2] if data else 0
    user_count_fetch = db.select_referal_count_new(user_id=call.message.chat.id)
    print(user_count_fetch, 'none')
    if not user_count_fetch:
        db.add_increment_fetch_new_count(user_id=call.message.chat.id, count=reklama_count)
    await call.message.answer(
    f'{_("Siz taklif qilgan do‘stlar soni:")} {taklif_qilganlar}\n'
    f'{_("Qolgan bepul limittingiz:")} {user_count_fetch[1]}\n\n',
    reply_markup=referal_button())
# f"✨ Har bir yangi do‘stingiz uchun 10 ta qo‘shimcha bepul limit qo‘lga kiriting! 📢",




@dp.callback_query(F.data == "referal_offer")
async def referal_offer(call: types.CallbackQuery):
    btn = InlineKeyboardBuilder()
    btn.button(text=_("back_to_main_menu"), callback_data="main_menu_back_referal")
    await call.answer(cache_time=60)
    
    data = db.select_referal_by_user_id(user_id=call.from_user.id)  
    
    if data:
        await call.message.answer(
            text=f'{_("Sizning referal kodingiz:")}\n'
                 f'{_("👥 Havolani dostlaringizga yuborib bepul limit oling")}\n\n'
                 f"{(f'https://t.me/{BOT_USERNAME}?start={data[3]}')}",
        reply_markup=btn.as_markup(), disable_web_page_preview=True)
        return
    
    shifr_code = base64.b64encode(str(call.from_user.id).encode()).decode()
    
    db.add_referal(user_id=call.from_user.id, referal_code=shifr_code)
    
    await call.message.answer(
        text=f'{_("Sizning referal kodingiz:")}\n'
             f'{_("👥 Havolani dostlaringizga yuborib bepul limit oling")}\n\n'
             f'{(f"https://t.me/{BOT_USERNAME}?start={shifr_code}")}',
    reply_markup=btn.as_markup(), disable_web_page_preview=True)
