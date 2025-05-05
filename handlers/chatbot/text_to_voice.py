from aiogram.fsm.context import FSMContext
from loader import dp, db
from aiogram import types, F
from data.config import OPENAI_KEY
from openai import OpenAI
from loader import bot
from aiogram.enums.chat_action import ChatAction
from states.my_state import Text_To_Voice
from filters.my_filter import MyFilter
import time
import os
from handlers.channels.fetch_count import is_fetch_limit_reached
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types.web_app_info import WebAppInfo
from data.config import MINI_APP_URL
from handlers.webapp.app import random_webapp_url
from keyboards.default.button import menu_button
import asyncio
import io
from aiogram.utils.i18n import gettext as _
from pathlib import Path
from keyboards.default.button import voices_button


BASE_DIR = Path(__file__).resolve().parent.parent.parent

client = OpenAI(
    api_key=OPENAI_KEY
)


languages = {
    # Turk tillari
    "Uzbek 🇺🇿": "uz",
    "Turkish 🇹🇷": "tr",
    "Kazakh 🇰🇿": "kk",
    "Azerbaijani 🇦🇿": "az",
    "Turkmen 🇹🇲": "tk",
    "Tatar 🇷🇺": "tt",
    "Kyrgyz 🇰🇬": "ky",
    "Uighur 🇨🇳": "ug",
    
    # Yevropa tillari
    "English 🇬🇧": "en",
    "Russian 🇷🇺": "ru",
    "French 🇫🇷": "fr",
    "German 🇩🇪": "de",
    "Spanish 🇪🇸": "es",
    "Italian 🇮🇹": "it",
    "Portuguese 🇵🇹": "pt",
    "Dutch 🇳🇱": "nl",
    "Polish 🇵🇱": "pl",
    "Ukrainian 🇺🇦": "uk",
    "Greek 🇬🇷": "el",
    "Swedish 🇸🇪": "sv",
    "Finnish 🇫🇮": "fi",
    "Danish 🇩🇰": "da",
    "Norwegian 🇳🇴": "no",
    "Hungarian 🇭🇺": "hu",
    "Czech 🇨🇿": "cs",
    "Slovak 🇸🇰": "sk",
    "Romanian 🇷🇴": "ro",
    "Serbian 🇷🇸": "sr",
    "Croatian 🇭🇷": "hr",
    "Bulgarian 🇧🇬": "bg",
    "Albanian 🇦🇱": "sq",
    "Lithuanian 🇱🇹": "lt",
    "Latvian 🇱🇻": "lv",
    "Estonian 🇪🇪": "et",
    "Belarusian 🇧🇾": "be",
    "Basque 🇪🇸": "eu",
    "Catalan 🇪🇸": "ca",
    "Irish 🇮🇪": "ga",
    "Scottish Gaelic 🏴": "gd",
    "Welsh 🏴": "cy",
    
    # Osiyo tillari
    "Chinese 🇨🇳": "zh",
    "Japanese 🇯🇵": "ja",
    "Korean 🇰🇷": "ko",
    "Mongolian 🇲🇳": "mn",
    "Tajik 🇹🇯": "tg",
    "Hindi 🇮🇳": "hi",
    "Bengali 🇧🇩": "bn",
    "Urdu 🇵🇰": "ur",
    "Persian 🇮🇷": "fa",
    "Pashto 🇦🇫": "ps",
    "Punjabi 🇮🇳": "pa",
    "Tamil 🇮🇳": "ta",
    "Telugu 🇮🇳": "te",
    "Marathi 🇮🇳": "mr",
    "Gujarati 🇮🇳": "gu",
    "Malayalam 🇮🇳": "ml",
    "Kannada 🇮🇳": "kn",
    "Sinhala 🇱🇰": "si",
    "Nepali 🇳🇵": "ne",
    "Thai 🇹🇭": "th",
    "Lao 🇱🇦": "lo",
    "Burmese 🇲🇲": "my",
    "Khmer 🇰🇭": "km",
    "Vietnamese 🇻🇳": "vi",
    "Malay 🇲🇾": "ms",
    "Indonesian 🇮🇩": "id",
    "Filipino 🇵🇭": "fil",
    "Hebrew 🇮🇱": "he",
    "Georgian 🇬🇪": "ka",
    "Armenian 🇦🇲": "hy",
    
    # Arab va Afrika tillari
    "Arabic 🇸🇦": "ar",
    "Swahili 🇰🇪": "sw",
    "Amharic 🇪🇹": "am",
    "Hausa 🇳🇬": "ha",
    "Yoruba 🇳🇬": "yo",
    "Igbo 🇳🇬": "ig",
    "Zulu 🇿🇦": "zu",
    "Xhosa 🇿🇦": "xh",
    "Afrikaans 🇿🇦": "af",
    "Somali 🇸🇴": "so",
    "Berber 🇲🇦": "ber",
    
    # Amerika va Okeaniya tillari
    "Hawaiian 🇺🇸": "haw",
    "Maori 🇳🇿": "mi",
    "Samoan 🇼🇸": "sm",
    "Tongan 🇹🇴": "to",
    "Quechua 🇵🇪": "qu",
    "Aymara 🇧🇴": "ay",
    "Guarani 🇵🇾": "gn",
    
    # Sun'iy va maxsus tillar
    "Esperanto 🌍": "eo",
    "Latin 🇻🇦": "la",
    "↩️ Orqaga": "back_button_translate"
}


PER_PAGE = 10

async def generate_text_to_voice(user_prompt, voicer, lang_name):
    translation_prompt = f"Quyidagi matnni {lang_name} tiliga aniq tarjima qiling. Faqat tarjima, hech qanday qo‘shimcha izohsiz!"
    translated_text = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "user", "content": f"{translation_prompt}\n\nMatn: {user_prompt}"}
        ],
        temperature=0.0  # To‘g‘ri tarjima uchun haroratni minimal darajaga tushiramiz
    ).choices[0].message.content

    print(f"Tarjima matn: {translated_text}")
    try:
        response = client.audio.speech.create(
            model='tts-1-hd',
            input=translated_text,
            voice=voicer
        )
        return response
    except Exception as e:
        return f"Xatolik yuz berdi: {str(e)}"
    
@dp.callback_query(F.data == "main_menu_back")
async def get_back(call: types.CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    await state.clear()
    await call.message.answer(text=_("main_menu"), reply_markup=menu_button())

@dp.callback_query(lambda query: query.data == "text_generate_voice")
async def generate_image(call: types.CallbackQuery, state: FSMContext,  page: int = 0):
    await call.answer(cache_time=60)
    btn = InlineKeyboardBuilder()
    keys = list(languages.keys())
    
    start = page * PER_PAGE
    end = start + PER_PAGE
    current_languages = keys[start:end]

    for lang in current_languages:
        btn.button(text=lang, callback_data=f"language5_{languages[lang]}")
    
    nav_buttons = []
    if page > 0:
        nav_buttons.append(types.InlineKeyboardButton(text=_("previous_button"), callback_data=f"page5_{page - 1}"))
    if end < len(keys):
        nav_buttons.append(types.InlineKeyboardButton(text=_("next_button"), callback_data=f"page5_{page + 1}"))
    
    # Orqaga tugmasi
    nav_buttons.append(types.InlineKeyboardButton(text=_("back_to_main_menu"), callback_data="language_back_button_translate"))

    btn.row(*nav_buttons)  
    btn.adjust(2)  
    await call.message.answer(text=_("choose_translation_language"), reply_markup=btn.as_markup())
    await state.set_state(Text_To_Voice.start)
    

@dp.callback_query(F.data.startswith("page5_"))
async def pagination_handler(call: types.CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    page = int(call.data.split("_")[1])
    await call.message.edit_text(text=_("choose_translation_language"), reply_markup=await get_language_menu3(page))
    await state.set_state(Text_To_Voice.start)

async def get_language_menu3(page: int):
    btn = InlineKeyboardBuilder()
    keys = list(languages.keys())
    
    start = page * PER_PAGE
    end = start + PER_PAGE
    current_languages = keys[start:end]

    for lang in current_languages:
        btn.button(text=lang, callback_data=f"language5_{languages[lang]}")
    
    nav_buttons = []
    if page > 0:
        nav_buttons.append(types.InlineKeyboardButton(text=_("previous_button"), callback_data=f"page3_{page - 1}"))
    if end < len(keys):
        nav_buttons.append(types.InlineKeyboardButton(text=_("next_button"), callback_data=f"page3_{page + 1}"))
    
    # Orqaga tugmasi
    nav_buttons.append(types.InlineKeyboardButton(text=_("back_to_main_menu"), callback_data="language_back_button_translate"))

    btn.row(*nav_buttons)
    btn.adjust(2)

    return btn.as_markup()

@dp.callback_query(Text_To_Voice.start, F.data.startswith('language5_'))
async def get_(call: types.CallbackQuery, state: FSMContext):
    lang_code = call.data.split("_")[1]  
    lang_name = next((key for key, value in languages.items() if value == lang_code), lang_code)
    print(lang_code, lang_name)
    await state.update_data(lang_name=lang_name, lang_code=lang_code)
    await state.set_state(Text_To_Voice.lang)
    await call.message.answer(text=_("Speakerni Tanlng !!!"), reply_markup=voices_button())

@dp.callback_query(F.data.startswith('voicer_'), Text_To_Voice.lang)
async def get_voicer(call: types.CallbackQuery, state: FSMContext):
    voicer = call.data.split('_')[-1]
    await state.update_data({'voicer': voicer})
    btn = InlineKeyboardBuilder()
    btn.button(text=_("back_to_main_menu"), callback_data="main_menu_back")
    await call.answer(cache_time=60)
    await call.message.answer(text=f'{_("send_text"),} \n\n{voicer}', reply_markup=btn.as_markup())
    await state.set_state(Text_To_Voice.voice)



@dp.message(Text_To_Voice.voice, MyFilter())
async def get_user_info(message: types.Message, state: FSMContext):
    button = InlineKeyboardBuilder()
    button.button(text=_("back_to_main_menu"), callback_data="main_menu_back")
    
    if message.text:
        info = await message.answer(text=_("text_to_voice_processing"))
        await bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.UPLOAD_VOICE)
        data = await state.get_data()
        voicer = data['voicer']
        lang_name = data['lang_name']
        response = await generate_text_to_voice(user_prompt=message.text, voicer=voicer, lang_name=lang_name)

        
        if isinstance(response, str):  
            await message.answer(text=response)
            await state.set_state(Text_To_Voice.voice)  
            return
        
        audio_bytes = io.BytesIO()
        for chunk in response.iter_bytes():
            audio_bytes.write(chunk)
        audio_bytes.seek(0)  

        try:
            voice = types.input_file.BufferedInputFile(audio_bytes.getvalue(), filename="output.mp3")

            file_path = f"{BASE_DIR}/media/text_to_voice/file_{time.time()}.mp3"
            with open(file_path, 'wb') as f:
                f.write(audio_bytes.getvalue())            
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
                db.add_chat(user_id=message.chat.id, voice=file_path, action="voice",  _state=f'{_("best_ai_bot")} {_("back_to_main_menu_other")}')
                db.delete_all_except_last_chat(message.chat.id)
                await state.set_state(Text_To_Voice.voice)
                return
            
            await message.reply_voice(voice=voice, caption=f'\n\n{_("best_ai_bot")}', reply_markup=button.as_markup())
            await state.set_state(Text_To_Voice.voice)
            await info.delete()
            audio_bytes.close()  
            if os.path.exists(file_path):
                os.remove(file_path)   
            return
        except Exception as e:
            print(e)
            await message.answer(text=_("send_text_again"), reply_markup=button.as_markup())
        finally:
            await state.set_state(Text_To_Voice.voice)

    else:
        await message.answer(text=_("please_send_text"), reply_markup=button.as_markup())
