from fastapi import FastAPI, Request
from loader import dp, bot, db
from aiogram import types
from app import setup_bot
import logging
import handlers
from utils.notify_admins import start,shutdown
from decouple import config
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
from aiogram import types
import os
from aiogram.utils.i18n import gettext as _
from aiogram.fsm.context import FSMContext
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
WEBHOOK_URL = config("WEBHOOK_URL")
# WEBHOOK_URL= "https://00be-213-206-61-193.ngrok-free.app"

WEBHOOK_PATH = f"bot/{bot.token}" 
WEBHOOK_ROOT = f"{WEBHOOK_URL}/{WEBHOOK_PATH}"

@app.on_event('startup')
async def start_project():
    await bot.delete_webhook()
    
    await bot.set_webhook(WEBHOOK_ROOT)
    
    await setup_bot()
    await start()
    logging.info("Bot started with Webhook!")
    print('Started...')

@app.get('/')
async def home():
    return "Hello World"

@app.post(f"/{WEBHOOK_PATH}")
async def webhook(request: Request):
    try:
        update = await request.json()
        update = types.Update(**update)
        await dp.feed_update(bot, update)
    except Exception as e:
        logging.error(f"Webhook error: {e}")
    return {"status": "success"}


@app.on_event('startup')
async def start_project():
    print('Shut down...')

from aiogram.fsm.storage.memory import MemoryStorage
from fastapi import Depends

from aiogram.utils.keyboard import InlineKeyboardBuilder
storage = MemoryStorage()  

async def get_fsm_context(user_id: str) -> FSMContext:
    return FSMContext(storage=storage, key=str(user_id))  

@app.post('/update/{user_id}/')
async def update_user(user_id: str, state: FSMContext = Depends(lambda user_id: get_fsm_context(user_id))):
    try:
        db.update_user_fetch(user_id)
        get_data = db.get_last_chat(user_id=user_id)
        print(get_data, 'get dara')
        data = get_data[-1].split(" ")
        print(data)
        print(data)
        if data[-1] == "home":
            btn = InlineKeyboardBuilder()
            btn.button(text=f"{data[1]}", callback_data="back_to_main_menu_other")
            if get_data[-2] == "text":
                await bot.send_message(chat_id=user_id, text=f'{get_data[1]} \n\n{data[0]}')
                return
            if get_data[-2] == "image":
                await bot.send_message(chat_id=user_id, text=f'{get_data[1]} \n\n{data[0]}')
                return
            if get_data[-2] == "voice":            
                file_path = get_data[2] 
                if os.path.exists(file_path):  
                    try:
                        await bot.send_audio(
                            chat_id=user_id,
                            audio=types.FSInputFile(file_path),
                            caption=f"\n\n{data[0]}",
                            reply_markup=btn.as_markup()
                        )
                    except Exception as e:
                        print(f"❌ Xatolik: {e}")
                else:
                    print(f"⚠️ Fayl topilmadi: {file_path}")
            if get_data[-2] == "voice_to_text":
                await bot.send_message(chat_id=user_id, text=f'{get_data[1]} \n\n{data[0]}')
                return
            if get_data[-2] == "document":
                await bot.send_message(chat_id=user_id, text=f'{get_data[1]} \n\n{data[0]}')
                return
            if get_data[-2] == "summar":
                await bot.send_message(chat_id=user_id, text=f'{get_data[1]} \n\n{data[0]}')
                return
            if get_data[-2] == "translate1":
                await bot.send_message(chat_id=user_id, text=f'{get_data[1]} \n\n{data[0]}')
            if get_data[-2] == "translate2":
                await bot.send_message(chat_id=user_id, text=f'{get_data[1]} \n\n{data[0]}')
        else:
            btn = InlineKeyboardBuilder()
            btn.button(text=f"{data[1]}", callback_data="back_to_main_menu_other")
            if get_data[-2] == "text":
                await bot.send_message(chat_id=user_id, text=f'{get_data[1]} \n\n{data[0]}', reply_markup=btn.as_markup())
                return
            if get_data[-2] == "image":
                await bot.send_message(chat_id=user_id, text=f'{get_data[1]} \n\n{data[0]}', reply_markup=btn.as_markup())
                return
            if get_data[-2] == "voice":            
                file_path = get_data[2] 
                if os.path.exists(file_path):  
                    try:
                        await bot.send_audio(
                            chat_id=user_id,
                            audio=types.FSInputFile(file_path),
                            reply_markup=btn.as_markup(),
                            caption=f"\n\n{data[0]}"
                        )
                    except Exception as e:
                        print(f"❌ Xatolik: {e}")
                else:
                    print(f"⚠️ Fayl topilmadi: {file_path}")
            if get_data[-2] == "voice_to_text":
                await bot.send_message(chat_id=user_id, text=f'{get_data[1]} \n\n{data[0]}', reply_markup=btn.as_markup())
                return
            if get_data[-2] == "document":
                await bot.send_message(chat_id=user_id, text=f'{get_data[1]} \n\n{data[0]}', reply_markup=btn.as_markup())
                return
            if get_data[-2] == "summar":
                await bot.send_message(chat_id=user_id, text=f'{get_data[1]} \n\n{data[0]}', reply_markup=btn.as_markup())
                return
            if get_data[-2] == "translate1":
                await bot.send_message(chat_id=user_id, text=f'{get_data[1]} \n\n{data[0]}', reply_markup=btn.as_markup())
            if get_data[-2] == "translate2":
                await bot.send_message(chat_id=user_id, text=f'{get_data[1]} \n\n{data[0]}', reply_markup=btn.as_markup())
        print({"success": True, "message": "Fetch count updated"})
        return {"success": True, "message": "Fetch count updated"}
    except Exception as e:
        print({"success": False, "message": f"Yangilash xatolik: {str(e)}"})
        return {"success": False, "message": f"Yangilash xatolik: {str(e)}"}


async def next_state(state_, state: FSMContext):
    await state.set_state(state_)  

@app.post('/get/data/{user_id}/')
async def update_user(user_id: str):
    try:
        data = db.get_user_fetch_count(user_id=user_id)
        return {'user_id': data[0], 'fetch_count': data[1]}
    except Exception as e:
        print({"success": False, "message": f"Yangilash xatolik: {str(e)}"})
        return {"success": False, "message": f"Yangilash xatolik: {str(e)}"}

# from aiogram import F
# from keyboards.default.button import menu_button

# @dp.callback_query(F.data == "back_to_main_menu_other")
# async def back_menu(call: types.CallbackQuery):
#     await call.message.answer(f"⚙️", reply_markup=menu_button())