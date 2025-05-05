import aiohttp
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram import F, types
from loader import dp, bot, db
from states.my_state import Document_Q_A
import fitz
import docx
from openai import OpenAI
from data.config import OPENAI_KEY
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

async def extract_text_from_pdf(file_bytes):
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text = "\n".join(page.get_text("text") for page in doc)
    return text

async def extract_text_from_docx(file_bytes):
    doc = docx.Document(file_bytes)
    text = "\n".join([p.text for p in doc.paragraphs])
    return text

async def extract_text_from_txt(file_bytes):
    text = file_bytes.decode("utf-8")
    return text

async def extract_text(file_bytes, file_type):
    if file_type == "application/pdf":
        return await extract_text_from_pdf(file_bytes)
    elif file_type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword"]:
        return await extract_text_from_docx(file_bytes)
    elif file_type == "text/plain":
        return await extract_text_from_txt(file_bytes)
    else:
        return None
    

@dp.callback_query(F.data == "main_menu_back")
async def get_back(call: types.CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    await state.clear()
    await call.message.answer(text=_("main_menu"), reply_markup=menu_button())


@dp.callback_query(F.data == "document_q_a")
async def get_doc(call: types.CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    btn = InlineKeyboardBuilder()
    btn.button(text=_("back_to_main_menu"), callback_data="main_menu_back")
    await call.message.answer(text=_("send_document"), reply_markup=btn.as_markup())
    await state.set_state(Document_Q_A.start)

@dp.message(Document_Q_A.start, MyFilter())
async def get_doc_data(msg: Message, state: FSMContext):
    await bot.send_chat_action(chat_id=msg.chat.id, action=ChatAction.TYPING)
    button = InlineKeyboardBuilder()
    button.button(text=_("back_to_main_menu"), callback_data="main_menu_back")
    if not msg.document:
        await msg.answer(_("please_send_document"), reply_markup=button.as_markup())
        return

    file_id = msg.document.file_id
    file_type = msg.document.mime_type

    try:
        file = await bot.get_file(file_id=file_id)
        file_url = f"https://api.telegram.org/file/bot{bot.token}/{file.file_path}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(file_url) as response:
                    if response.status == 200:
                        file_bytes = await response.read()

                        text = await extract_text(file_bytes, file_type)

                        if not text.strip():
                            await msg.answer(text=_("no_text_found"), reply_markup=button.as_markup())
                            return

                        await state.update_data(document_text=text)
                        await msg.answer(_("ask_document_info"), reply_markup=button.as_markup())
                        await state.set_state(Document_Q_A.final)
        except Exception as e:
            print(e)
        finally:
            await session.close()

    except Exception as e:
        await msg.answer(f"Xatolik yuz berdi: {str(e)}", reply_markup=button.as_markup())
        await state.clear() 

@dp.message(Document_Q_A.final, MyFilter())
async def get_final_q(msg: Message, state: FSMContext):
    button = InlineKeyboardBuilder()
    button.button(text=_("back_to_main_menu"), callback_data="main_menu_back")
    try:
        if not msg.text:
            await msg.answer(_("ask_what_needed_from_document"), reply_markup=button.as_markup())
            return

        data = await state.get_data()
        document_text = data.get("document_text", "")

        if not document_text:
            await msg.answer(_("document_text_not_found"), reply_markup=button.as_markup())
            return

        user_prompt = f"Hujjat matni:\n{document_text[:4000]}\n\nSavol: {msg.text}"
        await bot.send_chat_action(chat_id=msg.chat.id, action=ChatAction.TYPING)
        response = client.chat.completions.create(
            model='gpt-4',
            messages=[{"role": "user", "content": user_prompt}]
        )
        # check = is_fetch_limit_reached(msg.from_user.id)
        # if not check:
        # data = db.get_user_fetch_count_new(user_id=msg.from_user.id)
        # if data[0] == 0:
        #     # webapp_url = await random_webapp_url(msg.from_user.id)
        #     # btn = InlineKeyboardBuilder()
        #     # btn.button(text=_("get_answer_button"), web_app=WebAppInfo(url=webapp_url))
        #     # await msg.answer(text=_("press_button_to_get_answer"), reply_markup=btn.as_markup())
        #     btn = InlineKeyboardBuilder()
        #     btn.button(text=_("👥 Do'st taklif qilish"), callback_data="referal_offer")
        #     btn.button(text=_("back_to_main_menu"), callback_data="back_to_main_menu_other")
        #     btn.adjust(1)
        #     await msg.answer(text=_("Bepul limit olish uchun dostingiz taklif qiling"), reply_markup=btn.as_markup())
        #     db.update_user_fetch_new(user_id=msg.chat.id)
        #     db.add_chat(user_id=msg.chat.id, _text=response.choices[0].message.content, action="document",   _state=f'{_("best_ai_bot")} {_("back_to_main_menu_other")}')
        #     db.delete_all_except_last_chat(user_id=msg.chat.id)
        #     await state.set_state(Document_Q_A.start)

        #     return
        await msg.answer(f'{response.choices[0].message.content} \n\n{_("best_ai_bot")}', reply_markup=button.as_markup())
        await state.set_state(Document_Q_A.start)
        return

    except Exception as e:
        await msg.answer(f"Xatolik yuz berdi: {str(e)}", reply_markup=button.as_markup())

    finally:
        await state.clear()