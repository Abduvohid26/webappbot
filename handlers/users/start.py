from aiogram.filters import CommandStart, Command, CommandObject
from loader import dp, db, BASE_DIR
from aiogram import types, F, html
from data.config import OPENAI_KEY, BOT_TOKEN, MINI_APP_URL
from openai import OpenAI, RateLimitError
import asyncio
from loader import bot
from aiogram.enums.chat_action import ChatAction
from keyboards.default.button import menu_button
from filters.my_filter import MyFilter, IsAdmin
from middlewares.my_middleware import CheckSubCallback
from utils.misc.subscription import checksubscription
from handlers.channels.fetch_count import is_fetch_limit_reached
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types.web_app_info import WebAppInfo
from handlers.webapp.app import random_webapp_url
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _
from aiogram.types import FSInputFile
from check_url import get_db
import base64

client = OpenAI(
    api_key=OPENAI_KEY
)

@dp.message(CommandStart())
async def start_bot(message: types.Message):
    args = message.text.split()
    if len(args) == 2:
        referal_code = args[1]
        try:
            decoded_user = base64.b64decode(referal_code).decode('utf-8')
            if db.select_user(telegram_id=int(decoded_user)) and not db.select_user(telegram_id=message.from_user.id):
                await bot.send_message(text=f"{message.from_user.full_name}: Dostingizni taklif qilganingiz uchun 10 ta bepul limit oldingiz", chat_id=int(decoded_user))
                count_reklam = db.select_all_reklama()[0][1]
                db.update_user_fetch_new_zero_one(user_id=decoded_user, count=count_reklam)
                db.increament_referal_count(user_id=int(decoded_user))
            else:
                pass
        except Exception as e:
            print(f"Xatoli: {e}")
    if db.select_user(telegram_id=message.from_user.id):
        link = f"tg://user?id={message.from_user.id}"
        user_lang = message.from_user.language_code
        # salom_message = f"👋 Assalamu Aleykum {html.bold(value=html.link(value=message.from_user.full_name, link=link))} \nSizga qanday yordam bera olishim mumkin? 🤖💬"
        salom_message = _("start_message").format(name=f"{html.bold(value=html.link(value=message.from_user.full_name, link=link))}")
        await message.answer(salom_message, reply_markup=menu_button())
        btn = InlineKeyboardBuilder()
        webapp_url = await random_webapp_url(message.from_user.id)

        btn.button(text="📝 Javobni olish", web_app=WebAppInfo(url=webapp_url))
        await message.answer(text="Javobni olish uchun tugmani bosing 🔒", reply_markup=btn.as_markup())
        await message.answer("Test", reply_markup=btn.as_markup())
        return
    await get_db()
    user = message.from_user
    db.add_user(fullname=user.full_name, telegram_id=user.id, language=user.language_code)
    link = f"tg://user?id={message.from_user.id}"

    salom_message = _("start_message").format(name=f"{html.bold(value=html.link(value=message.from_user.full_name, link=link))}")

    await message.answer(salom_message, reply_markup=menu_button())
    btn = InlineKeyboardBuilder()
    webapp_url = await random_webapp_url(message.from_user.id)

    btn.button(text="📝 Javobni olish", web_app=WebAppInfo(url=webapp_url))
    await message.answer(text="Javobni olish uchun tugmani bosing 🔒", reply_markup=btn.as_markup())
    await message.answer("Test", reply_markup=btn.as_markup())

async def generate_response(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": f"Qisqa va aniq javob ber: {prompt}"}
            ]
        )
        return response.choices[0].message.content
    except RateLimitError:
        await asyncio.sleep(5)
        return await generate_response(prompt)
    except Exception as e:
        return f"Xatolik yuz berdi: {str(e)}"

@dp.message(Command('database'), IsAdmin())
async def send_database(msg: types.Message):
    db_path = "data/main.db"
    db_file = FSInputFile(path=db_path)
    await msg.answer_document(db_file)
    

# @dp.message(F.text, MyFilter())
# async def send_welcome(message: types.Message):
#     user_message = message.text
#     await bot.send_chat_action(chat_id=message.chat.id, action="typing")
#     db.add_chat(user_id=message.chat.id, _text=response)
#     db.delete_all_except_last_chat(message.chat.id)
    

#     try:
#         response = await generate_response(user_message)
#         limit_reached = is_fetch_limit_reached(message.from_user.id)  
        
#         if limit_reached == False:
#             webapp_url = await random_webapp_url(message.chat.id)
#             btn = InlineKeyboardBuilder()
#             btn.button(text="📝 Javobni olish", web_app=WebAppInfo(url=webapp_url))
#             await message.answer(text="1Javobni olish uchun tugmani bosing 🔒", reply_markup=btn.as_markup())
#             db.add_chat(user_id=message.chat.id, _text=response, action="text")
#             db.delete_all_except_last_chat(message.chat.id)
#             return
        
#         await message.reply(response)

#     except Exception as e:
#         await message.reply(f"Xatolik yuz berdi: {str(e)}")
@dp.message(F.text, MyFilter())
async def send_welcome(message: types.Message):
    user_message = message.text
    user_id = message.chat.id 
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    datas = db.select_all_chats_bots(user_id=message.from_user.id)
    context = []
    if datas is not None:
        for data in datas:
            if data[-1] == "user":
                context.append({"role": "user", "content": data[1]})
                continue
            context.append({"role": "assistant", "content": data[1]})
    context.append({"role": "user", "content": user_message})
    messages = [
        {"role": "system", "content": "Sen sotib olingan API san va chat tarixini o'zing saqlamaysan, shuning uchun men senga har safar oldingi chat tarixini yuboraman. Sen faqat yangi berilgan savolga javob berishing kerak."}
    ]
    messages.extend(context)  
    messages.append({"role": "user", "content": user_message}) 


    try:
        bot_res = client.chat.completions.create(
            model="gpt-4",  
            messages=messages,
        )
        response = bot_res.choices[0].message.content

        try:
            db.add_chat_or_bot(user_id=user_id, message=user_message, role="user")
            db.add_chat_or_bot(user_id=user_id, message=response, role="assistant")
            db.delete_all_old_chat(user_id)
        except Exception as e:
            print(e, "xatolik")

        # Limiti tekshirish
        limit_reached = is_fetch_limit_reached(message.from_user.id)
        # if limit_reached == False:
        #1 data = db.get_user_fetch_count_new(user_id=message.from_user.id)
        #1 if data[0] == 0:
        #     # webapp_url = await random_webapp_url(message.from_user.id)
        #     # print(webapp_url)
        #     btn = InlineKeyboardBuilder()
        #     # btn.button(text=_("get_answer_button"), web_app=WebAppInfo(url=webapp_url))
        #     # await message.answer(text=_("press_button_to_get_answer"), reply_markup=btn.as_markup())
        #     btn.button(text=_("👥 Do'st taklif qilish"), callback_data="referal_offer")
        #     btn.button(text="🎁 Premium tarif", callback_data="referal_premium")
        #     btn.button(text=_("back_to_main_menu"), callback_data="back_to_main_menu_other")
        #     btn.adjust(1)
        #     await message.answer(text=_("Bepul limit olish uchun dostingiz taklif qiling"), reply_markup=btn.as_markup())
        #     db.add_chat(user_id=message.chat.id, _text=response, action="text",  _state=f'{_("best_ai_bot")} {_("back_to_main_menu_other")} home')
        #     db.delete_all_except_last_chat(message.chat.id)
        #     return
        # db.update_user_fetch_new(user_id=message.chat.id)
        await message.reply(f'{response} \n\n{_("best_ai_bot")}')
    except Exception as e:
        await message.reply(f"Xatolik yuz berdi: {str(e)}")




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

@dp.message(F.photo, MyFilter())
async def handle_photo(message: types.Message):
    button = InlineKeyboardBuilder()
    button.button(text=_("back_to_main_menu"), callback_data="main_menu_back")
    try:
        photo_file = await bot.get_file(message.photo[-1].file_id)
        photo_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{photo_file.file_path}"
        await bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
        caption = message.caption if message.caption else None
        analysis_result = await analyze_image(photo_url, caption)
        # check = is_fetch_limit_reached(message.from_user.id)
        # if not check:
        data = db.get_user_fetch_count_new(user_id=message.from_user.id)
        if data[0] == 0:
            # webapp_url = await random_webapp_url(message.from_user.id)
            btn = InlineKeyboardBuilder()
            # btn.button(text=_("get_answer_button"), web_app=WebAppInfo(url=webapp_url))
            # await message.answer(text=_("press_button_to_get_answer"), reply_markup=btn.as_markup())
            btn.button(text=_("👥 Do'st taklif qilish"), callback_data="referal_offer")
            btn.button(text=_("back_to_main_menu"), callback_data="back_to_main_menu_other")
            btn.adjust(1)
            await message.answer(text=_("Bepul limit olish uchun dostingiz taklif qiling"), reply_markup=btn.as_markup())
            db.add_chat(user_id=message.chat.id, image=message.photo[-1].file_id, action="image", _text=analysis_result,  _state=f'{_("best_ai_bot")} {_("back_to_main_menu_other")}')
            db.delete_all_except_last_chat(message.chat.id)
            return
        db.update_user_fetch_new(user_id=message.chat.id)
        await message.reply(f'{analysis_result} \n\n{_("best_ai_bot")}')
    except Exception as e:
        await message.reply(f"Xatolik yuz berdi: {str(e)}", reply_markup=button.as_markup())



@dp.message(MyFilter())
async def get_messages(msg: types.Message):
    link = f"tg://user?id={msg.from_user.id}"
    await msg.answer(
    _(
        "salom_message_none"
    ).format(
        full_name=html.bold(value=html.link(value=msg.from_user.full_name, link=link))
    )
)


@dp.callback_query(CheckSubCallback.filter())
async def check_query(call: types.CallbackQuery):
    await call.answer(cache_time=0)
    user = call.from_user
    final_status = True
    btn = InlineKeyboardBuilder()

    await call.message.delete()
    CHANNELS = db.select_all_channels()
    if CHANNELS:
        for channel in CHANNELS:
            try:
                status = await checksubscription(user_id=user.id, channel=channel[-1])
                final_status = final_status and status
                chat = await bot.get_chat(chat_id=channel[-1])
                invite_link = await chat.export_invite_link()
                btn.button(
                    text=f"{'✅' if status else '❌'} {chat.title}",
                    url=invite_link
                )
            except Exception as e:
                print(f"Kanalga kirish yoki linkni olishda xato: {e}")

        if final_status:
            args = call.message.text.split()
            if len(args) == 2:
                referal_code = args[1]
                try:
                    decoded_user = base64.b64decode(referal_code).decode('utf-8')
                    if db.select_user(telegram_id=int(decoded_user)) and not db.select_user(telegram_id=call.message.from_user.id):
                        await bot.send_message(text=f"{call.message.from_user.full_name}: Dostingizni taklif qilganingiz uchun 10 ta bepul limit oldingiz", chat_id=int(decoded_user))
                        count_reklam = db.select_all_reklama()[0][1]
                        db.update_user_fetch_new_zero_one(user_id=decoded_user, count=count_reklam)
                        db.increament_referal_count(user_id=int(decoded_user))
                    else:
                        pass
                except Exception as e:
                    print(f"Xatoli: {e}")
            if db.select_user(telegram_id=call.message.from_user.id):
                link = f"tg://user?id={call.message.from_user.id}"

                # salom_message = f"👋 Assalamu Aleykum {html.bold(value=html.link(value=call.message.from_user.full_name, link=link))} \nSizga qanday yordam bera olishim mumkin? 🤖💬"
                salom_message = _("start_message").format(name=f"{html.bold(value=html.link(value=call.message.from_user.full_name, link=link))}")

                await call.message.answer(salom_message, reply_markup=menu_button())
                return
            await get_db()
            user = call.message.from_user
            db.add_user(fullname=user.full_name, telegram_id=user.id, language=user.language_code)
            link = f"tg://user?id={call.message.from_user.id}"
            salom_message = _("start_message").format(name=f"{html.bold(value=html.link(value=call.message.from_user.full_name, link=link))}")
            # salom_message = f"👋 Assalamu Aleykum {html.bold(value=html.link(value=call.message.from_user.full_name, link=link))} \nSizga qanday yordam bera olishim mumkin? 🤖💬"

            await call.message.answer(salom_message, reply_markup=menu_button())
        else:
            btn.button(
                text=_("check_subscription"),
                callback_data=CheckSubCallback(check=False)
            )
            btn.adjust(1)
            await call.message.answer(
                text=_("please_join_all_channels"),
                reply_markup=btn.as_markup()
            )
    else:
        args = call.message.text.split()
        if len(args) == 2:
            referal_code = args[1]
            try:
                decoded_user = base64.b64decode(referal_code).decode('utf-8')
                if db.select_user(telegram_id=int(decoded_user)) and not db.select_user(telegram_id=call.message.from_user.id):
                    await bot.send_message(text=f"{call.message.from_user.full_name}: Dostingizni taklif qilganingiz uchun 10 ta bepul limit oldingiz", chat_id=int(decoded_user))
                    count_reklam = db.select_all_reklama()[0][1]
                    db.update_user_fetch_new_zero_one(user_id=decoded_user, count=count_reklam)
                    db.increament_referal_count(user_id=int(decoded_user))
                else:
                    pass
            except Exception as e:
                print(f"Xatoli: {e}")
        if db.select_user(telegram_id=call.message.from_user.id):
            link = f"tg://user?id={call.message.from_user.id}"

            # salom_message = f"👋 Assalamu Aleykum {html.bold(value=html.link(value=call.message.from_user.full_name, link=link))} \nSizga qanday yordam bera olishim mumkin? 🤖💬"
            salom_message = _("start_message").format(name=f"{html.bold(value=html.link(value=call.message.from_user.full_name, link=link))}")
            await call.message.answer(salom_message, reply_markup=menu_button())
            return
        await get_db()
        user = call.message.from_user
        db.add_user(fullname=user.full_name, telegram_id=user.id, language=user.language_code)
        link = f"tg://user?id={call.message.from_user.id}"
        salom_message = _("start_message").format(name=f"{html.bold(value=html.link(value=call.message.from_user.full_name, link=link))}")

        # salom_message = f"👋 Assalamu Aleykum {html.bold(value=html.link(value=call.message.from_user.full_name, link=link))} \nSizga qanday yordam bera olishim mumkin? 🤖💬"

        await call.message.answer(salom_message, reply_markup=menu_button())



@dp.callback_query(F.data == "back_to_main_menu_other")
async def back_menu(call: types.CallbackQuery):
    await call.answer(cache_time=60)
    await call.message.answer(f"Main", reply_markup=menu_button())


