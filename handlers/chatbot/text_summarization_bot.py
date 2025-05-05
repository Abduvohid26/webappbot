from aiogram.fsm.context import FSMContext
from loader import dp, db
from aiogram import types, F
from data.config import OPENAI_KEY
from openai import OpenAI
from loader import bot
from states.my_state import Text_Summar
from filters.my_filter import MyFilter
from aiogram.enums.chat_action import ChatAction
from handlers.channels.fetch_count import is_fetch_limit_reached
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types.web_app_info import WebAppInfo
from data.config import MINI_APP_URL
import asyncio
from handlers.webapp.app import random_webapp_url
from keyboards.default.button import menu_button
from aiogram.utils.i18n import gettext as _

client = OpenAI(api_key=OPENAI_KEY)


def chunk_text(text, chunk_size=4096):
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
    return chunks


@dp.callback_query(F.data == "text_summarization_bot")
async def text_summarization(call: types.CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    btn = InlineKeyboardBuilder()
    btn.button(text=_("back_to_main_menu"), callback_data="main_menu_back")
    text = _("text_summarization_intro")
    await call.message.answer(text, reply_markup=btn.as_markup())
    await state.set_state(Text_Summar.start)


@dp.callback_query(F.data == "main_menu_back")
async def get_back(call: types.CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    await state.clear()
    await call.message.answer(text=_("main_menu"), reply_markup=menu_button())


@dp.message(Text_Summar.start, MyFilter())
async def summarize_text(message: types.Message, state: FSMContext):
    await bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
    button = InlineKeyboardBuilder()
    button.button(text=_("back_to_main_menu"), callback_data="main_menu_back")
    if message.text:
        user_prompt = message.text
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": f"{_('summarize_text')} ->: {user_prompt}"}
            ]
        )
        # check = is_fetch_limit_reached(message.from_user.id)
        # if not check:
        data = db.get_user_fetch_count_new(user_id=message.from_user.id)
        if data[0] == 0:
            # webapp_url = await random_webapp_url(message.from_user.id)
            # btn = InlineKeyboardBuilder()
            # btn.button(text=_("get_answer_button"), web_app=WebAppInfo(url=webapp_url))
            # await message.answer(text=_("press_button_to_get_answer"), reply_markup=btn.as_markup())
            btn = InlineKeyboardBuilder()
            btn.button(text=_("👥 Do'st taklif qilish"), callback_data="referal_offer")
            btn.button(text=_("back_to_main_menu"), callback_data="back_to_main_menu_other")
            btn.adjust(1)
            await message.answer(text=_("Bepul limit olish uchun dostingiz taklif qiling"), reply_markup=btn.as_markup())
            db.update_user_fetch_new(user_id=message.chat.id)
            db.add_chat(user_id=message.chat.id, _text=response.choices[0].message.content, action="summar",   _state=f'{_("best_ai_bot")} {_("back_to_main_menu_other")}')
            db.delete_all_except_last_chat(message.chat.id)
            await state.set_state(Text_Summar.start)

            return
        await message.answer(text=f'{response.choices[0].message.content} \n\n{_("best_ai_bot")}', reply_markup=button.as_markup())
        await state.set_state(Text_Summar.start)
        return
    await message.answer(text=_("please_send_text"), reply_markup=button.as_markup())