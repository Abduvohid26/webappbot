from aiogram.fsm.context import FSMContext
from loader import dp, db
from aiogram import types, F
from data.config import OPENAI_KEY, BOT_TOKEN
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


client = OpenAI(api_key=OPENAI_KEY)


async def analyze_image(image_url, caption: str = None):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"{caption if caption else 'Bu rasmda nima bor? Tafsirlang. qisqa mazmunda'}"},
                    {"type": "image_url", "image_url":  {"url": f"{image_url}", "detail": "low"}},
                ],
            }
        ],
    )
    return response.choices[0].message.content


@dp.callback_query(F.data == "main_menu_back")
async def get_back(call: types.CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    await state.clear()
    await call.message.answer(text=_("main_menu"), reply_markup=menu_button())


@dp.callback_query(F.data == 'analyze_image')
async def generate_image(call: types.CallbackQuery, state: FSMContext):
    btn = InlineKeyboardBuilder()
    btn.button(text=_("back_to_main_menu"), callback_data="main_menu_back")
    await call.answer(cache_time=60)
    await call.message.answer(text=_("send_image"), reply_markup=btn.as_markup())
    await state.set_state(Image_Analyze.start)


@dp.message(Image_Analyze.start, MyFilter())
async def get_user_info(message: types.Message, state: FSMContext):
    button = InlineKeyboardBuilder()
    button.button(text=_("back_to_main_menu"), callback_data="main_menu_back")
    if message.photo:
        info = await message.answer(text=_("image_processing"))
        await bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
        photo_file = await bot.get_file(message.photo[-1].file_id)
        photo_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{photo_file.file_path}"
        await bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
        caption = message.caption if message.caption else None
        analysis_result = await analyze_image(photo_url, caption)
        # check = is_fetch_limit_reached(message.from_user.id)
        # # if not check:
        # data = db.get_user_fetch_count_new(user_id=message.from_user.id)
        # if data[0] == 0:
        #     # webapp_url = await random_webapp_url(message.from_user.id)
        #     # btn = InlineKeyboardBuilder()
        #     # btn.button(text=_("get_answer_button"), web_app=WebAppInfo(url=webapp_url))
        #     # await message.answer(text=_("press_button_to_get_answer"), reply_markup=btn.as_markup())
        #     btn = InlineKeyboardBuilder()
        #     btn.button(text=_("👥 Do'st taklif qilish"), callback_data="referal_offer")
        #     btn.button(text=_("back_to_main_menu"), callback_data="back_to_main_menu_other")
        #     btn.adjust(1)
        #     await message.answer(text=_("Bepul limit olish uchun dostingiz taklif qiling"), reply_markup=btn.as_markup())
        #     db.add_chat(user_id=message.chat.id, image=message.photo[-1].file_id, action="image",  _text=analysis_result, _state=f'{_("best_ai_bot")} {_("back_to_main_menu_other")}')
        #     db.delete_all_except_last_chat(message.chat.id)
        #     await state.set_state(Image_Analyze.start)
        #     return
        # db.update_user_fetch_new(user_id=message.chat.id)
        await message.reply(f'{analysis_result} \n\n{_("best_ai_bot")}', reply_markup=button.as_markup())
        await state.set_state(Image_Analyze.start)
        await info.delete()
        return
    else:
        await message.answer(text=_("please_send_image"), reply_markup=button.as_markup())