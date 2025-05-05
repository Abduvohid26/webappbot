from aiogram.fsm.context import FSMContext
from loader import dp
from aiogram import types, F
from data.config import OPENAI_KEY
from openai import OpenAI
from loader import bot
from aiogram.enums.chat_action import ChatAction
from states.my_state import Generate_image_state
from filters.my_filter import MyFilter
from handlers.channels.fetch_count import is_fetch_limit_reached
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types.web_app_info import WebAppInfo
from data.config import MINI_APP_URL
import asyncio
from handlers.webapp.app import random_webapp_url
from keyboards.default.button import menu_button

client = OpenAI(
    api_key=OPENAI_KEY
)

async def generate_image_ai(user_prompt):
    try:
        response = client.images.generate(
            model='dall-e-3',
            prompt=user_prompt,
            size='1024x1024',
            quality='hd',
            n=1
        )
        return response.data[0].url
    except Exception as e:
        return f"Xatolik yuz berdi: {str(e)}"
    

@dp.callback_query(F.data == "main_menu_back")
async def get_back(call: types.CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    await state.clear()
    await call.message.answer(text=f"⚙️ Asosiy Menu", reply_markup=menu_button())



@dp.callback_query(lambda query: query.data == 'image_generate_bot')
async def generate_image(call: types.CallbackQuery, state: FSMContext):
    btn = InlineKeyboardBuilder()
    btn.button(text="↩️ Asosiy menu qaytish", callback_data="main_menu_back")
    await call.answer(cache_time=60)
    await call.message.answer(text="Rasm qanday ko'rinishda bo'lsin tarif yozing men tahlil sizga rasm yaratib beraman", reply_markup=btn.as_markup())
    await state.set_state(Generate_image_state.start)


@dp.message(Generate_image_state.start, MyFilter())
async def get_user_info(message: types.Message, state: FSMContext):
    button = InlineKeyboardBuilder()
    button.button(text="↩️ Asosiy menu qaytish", callback_data="main_menu_back")
    if message.text:
        await message.answer(text="Rasm generatsiya qilinyapti kuting ⌚️⏳")
        await bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.UPLOAD_PHOTO)
        url = await generate_image_ai(message.text)
        try:
            check = is_fetch_limit_reached(message.from_user.id)
            if not check:
                btn = InlineKeyboardBuilder()
                webapp_url = await random_webapp_url(message.from_user.id)
                btn.button(text="📝 Javobni olish", web_app=WebAppInfo(url=webapp_url))
                await message.answer(text="Javobni olish uchun tugmani bosing 🔒", reply_markup=btn.as_markup())
                await asyncio.sleep(15)
                await message.reply_photo(photo=url)
                return
            await message.reply_photo(photo=url)
            await state.clear()
        except Exception as e:
            await message.answer(text="Rasm haqida yozing please !!!", reply_markup=button.as_markup())
        return
    await message.answer(text="Iltimos, Rasm uchun tarif yozing !!!", reply_markup=button.as_markup())


