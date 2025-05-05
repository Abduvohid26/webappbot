from aiogram.fsm.context import FSMContext

from loader import dp, db
from aiogram import types, F
from data.config import OPENAI_KEY
from openai import OpenAI
from loader import bot
from aiogram.enums.chat_action import ChatAction
from states.my_state import Voice_To_Text
from filters.my_filter import MyFilter
import time
import os
from handlers.channels.fetch_count import is_fetch_limit_reached
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types.web_app_info import WebAppInfo
from data.config import MINI_APP_URL
import asyncio
from handlers.webapp.app import random_webapp_url
from keyboards.default.button import menu_button
from aiogram.utils.i18n import gettext as _
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent.parent


client = OpenAI(
    api_key=OPENAI_KEY
)

languages = {
    # Turk tillari
    "Uzbek 🇺🇿": "uz",
    "Turkish 🇹🇷": "tr",
    "Kazakh 🇰🇿": "kz",
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

async def generate_voice_to_text(user_prompt: str, lang_code: str = None, lang_name: str = None):
    supported_languages = {
        "en", "es", "fr", "de", "it", "pt", "nl", "ru", "pl", "sv", "tr",
        "hi", "ja", "ko", "zh", "ar", "he", "id", "fi", "cs", "uk", "hu", "ro"
    }
    print(lang_code, 'lang code')
    # translation_prompt = f"Translate the following text accurately into {lang_name}."

    # translated_text = client.chat.completions.create(
    #     model="gpt-4-turbo",
    #     messages=[
    #         {"role": "system", "content": translation_prompt},
    #         {"role": "user", "content": user_prompt}
    #     ],
    #     temperature=0.3
    # ).choices[0].message.content
    # print(f"Tarjima matn: {translated_text}")
    try:
        with open(user_prompt, "rb") as file:
            transcription_params = {
                "model": "whisper-1",
                "file": file,
            }
            if lang_code in supported_languages:
                transcription_params["language"] = lang_code

            response = client.audio.transcriptions.create(**transcription_params)
            translation_prompt = f"Quyidagi matnni {lang_name} tiliga aniq tarjima qiling."

            
            print(response.text)
            translated_text = client.chat.completions.create(
                model="chatgpt-4o-latest",
                messages=[
                    {"role": "system", "content": translation_prompt},
                    {"role": "user", "content": response.text}
                ],
                temperature=0.3
            ).choices[0].message.content
            print(translated_text)
            return translated_text
    except Exception as e:
        return f"Xatolik yuz berdi: {str(e)}"


@dp.callback_query(F.data == "main_menu_back")
async def get_back(call: types.CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    await state.clear()
    await call.message.answer(text=_("main_menu"), reply_markup=menu_button())


@dp.callback_query(F.data == 'voice_generate_text')
async def generate_voice(call: types.CallbackQuery, state: FSMContext, page: int = 0):
    await call.answer(cache_time=60)
    btn = InlineKeyboardBuilder()
    keys = list(languages.keys())
    
    start = page * PER_PAGE
    end = start + PER_PAGE
    current_languages = keys[start:end]

    for lang in current_languages:
        btn.button(text=lang, callback_data=f"language6_{languages[lang]}")
    
    nav_buttons = []
    if page > 0:
        nav_buttons.append(types.InlineKeyboardButton(text=_("previous_button"), callback_data=f"page6_{page - 1}"))
    if end < len(keys):
        nav_buttons.append(types.InlineKeyboardButton(text=_("next_button"), callback_data=f"page6_{page + 1}"))
    
    # Orqaga tugmasi
    nav_buttons.append(types.InlineKeyboardButton(text=_("back_to_main_menu"), callback_data="language_back_button_translate"))

    # Navigatsiya tugmalarini qo'shish
    btn.row(*nav_buttons)  
    btn.adjust(2)  
    await call.message.answer(text=_("choose_translation_language"), reply_markup=btn.as_markup())
    await state.set_state(Voice_To_Text.start)


@dp.callback_query(F.data.startswith("page6_"))
async def pagination_handler(call: types.CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    page = int(call.data.split("_")[1])
    await call.message.edit_text(text=_("choose_translation_language"), reply_markup=await get_language_menu3(page))
    await state.set_state(Voice_To_Text.start)

async def get_language_menu3(page: int):
    btn = InlineKeyboardBuilder()
    keys = list(languages.keys())
    
    start = page * PER_PAGE
    end = start + PER_PAGE
    current_languages = keys[start:end]

    for lang in current_languages:
        btn.button(text=lang, callback_data=f"language6_{languages[lang]}")
    
    nav_buttons = []
    if page > 0:
        nav_buttons.append(types.InlineKeyboardButton(text=_("previous_button"), callback_data=f"page6_{page - 1}"))
    if end < len(keys):
        nav_buttons.append(types.InlineKeyboardButton(text=_("next_button"), callback_data=f"page6_{page + 1}"))
    
    # Orqaga tugmasi
    nav_buttons.append(types.InlineKeyboardButton(text=_("back_to_main_menu"), callback_data="language_back_button_translate"))

    btn.row(*nav_buttons)
    btn.adjust(2)

    return btn.as_markup()

@dp.callback_query(Voice_To_Text.start)
async def get_lang(call: types.CallbackQuery, state: FSMContext):
    lang_code = call.data.split("_")[-1]  
    lang_name = next((key for key, value in languages.items() if value == lang_code), lang_code)
    print(lang_code, lang_name)
    await state.update_data(lang_name=lang_name, lang_code=lang_code)
    btn = InlineKeyboardBuilder()
    btn.button(text=_("back_to_main_menu"), callback_data="main_menu_back")
    await call.message.answer(text=_("voice_to_text"), reply_markup=btn.as_markup())
    await state.set_state(Voice_To_Text.lang)

@dp.message(Voice_To_Text.lang, MyFilter())
async def get_user_info(message: types.Message, state: FSMContext):
    button = InlineKeyboardBuilder()
    button.button(text=_("back_to_main_menu"), callback_data="main_menu_back")
    data = await state.get_data()
    lang_code = data['lang_code']
    lang_name = data['lang_name']
    if message.voice:
        info = await message.answer(text=_("voice_processing"))
        await bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
        file = await bot.get_file(file_id=message.voice.file_id)
        custom_file_name = f'{BASE_DIR}/media/voice_to_text/{time.time()}.mp3'
        await bot.download(file=file, destination=custom_file_name)        
        text = await generate_voice_to_text(custom_file_name, lang_code=lang_code, lang_name=lang_name)
        try:
            # check = is_fetch_limit_reached(message.from_user.id)
            # if not check:
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
            #     db.update_user_fetch_new(user_id=message.chat.id)
            #     db.add_chat(user_id=message.chat.id, _text=text, action="voice_to_text",   _state=f'{_("best_ai_bot")} {_("back_to_main_menu_other")}')
            #     db.delete_all_except_last_chat(message.chat.id)
            #     await state.set_state(Voice_To_Text.lang)
            #     return
            await message.reply(text=f'{text} \n\n{_("best_ai_bot")}', reply_markup=button.as_markup())
            await info.delete()
            await state.set_state(Voice_To_Text.lang)
        except Exception as e:
            await message.answer(text=_("send_voice_again"), reply_markup=button.as_markup())
        finally:
            await state.set_state(Voice_To_Text.lang)
            if os.path.exists(custom_file_name):
                os.remove(custom_file_name)
                return
    await message.answer(text=_("please_send_voice"), reply_markup=button.as_markup())

