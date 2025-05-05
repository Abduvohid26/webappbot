from aiogram.fsm.context import FSMContext
from loader import dp, db
from aiogram import types, F
from data.config import OPENAI_KEY
from openai import OpenAI
from loader import bot
from states.my_state import VoiceTranslate, LanguageStateVoice
from aiogram.enums.chat_action import ChatAction
from aiogram.utils.keyboard import InlineKeyboardBuilder
import aiohttp
import asyncio
from io import BytesIO
from aiogram.types import FSInputFile
from pathlib import Path
import time
import os
from keyboards.default.button import menu_button, voices_button

from handlers.channels.fetch_count import is_fetch_limit_reached
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types.web_app_info import WebAppInfo
from data.config import MINI_APP_URL
from handlers.webapp.app import random_webapp_url
from filters.my_filter import MyFilter

client = OpenAI(api_key=OPENAI_KEY)
BASE_DIR = Path(__file__).resolve().parent.parent.parent


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
from aiogram.utils.i18n import gettext as _


@dp.callback_query(F.data == 'language_back_button_translate')
async def back_button(call: types.CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    await call.answer(cache_time=60)
    await state.clear()
    await call.message.answer(text=_("back_to_main_menu"), reply_markup=menu_button())

@dp.callback_query(F.data == "voice_translate")
async def get_two_translate_start(call: types.CallbackQuery):
    await call.answer(cache_time=60)
    btn = InlineKeyboardBuilder()
    btn.button(text=_("🗣 Voice Translater V1"), callback_data="one_translate1")
    btn.button(text=_("🗣 Voice Translater V2"), callback_data="two_translate2")
    btn.adjust(1)
    await call.message.answer(text=_("choose_option"), reply_markup=btn.as_markup())

@dp.callback_query(F.data == "one_translate1")
async def send_language_menu(call: types.CallbackQuery, state: FSMContext,  page: int = 0, ):
    await call.answer(cache_time=60)
    btn = InlineKeyboardBuilder()
    keys = list(languages.keys())
    
    start = page * PER_PAGE
    end = start + PER_PAGE
    current_languages = keys[start:end]

    # Tillarni qo'shish
    for lang in current_languages:
        btn.button(text=lang, callback_data=f"language_{languages[lang]}")
    
    # Navigatsiya tugmalari
    nav_buttons = []
    if page > 0:
        nav_buttons.append(types.InlineKeyboardButton(text=_("previous_button"), callback_data=f"page3_{page - 1}"))
    if end < len(keys):
        nav_buttons.append(types.InlineKeyboardButton(text=_("next_button"), callback_data=f"page3_{page + 1}"))
    
    # Orqaga tugmasi
    nav_buttons.append(types.InlineKeyboardButton(text=_("back_to_main_menu"), callback_data="language_back_button_translate"))

    # Navigatsiya tugmalarini qo'shish
    btn.row(*nav_buttons)  
    btn.adjust(2)  
    await call.message.answer(text=_("choose_translation_language"), reply_markup=btn.as_markup())
    await state.set_state(VoiceTranslate.start)
    


@dp.callback_query(F.data.startswith("page3_"))
async def pagination_handler(call: types.CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    page = int(call.data.split("_")[1])
    await call.message.edit_text(text=_("choose_translation_language"), reply_markup=await get_language_menu3(page))
    await state.set_state(VoiceTranslate.start)

async def get_language_menu3(page: int):
    btn = InlineKeyboardBuilder()
    keys = list(languages.keys())
    
    start = page * PER_PAGE
    end = start + PER_PAGE
    current_languages = keys[start:end]

    for lang in current_languages:
        btn.button(text=lang, callback_data=f"language_{languages[lang]}")
    
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


@dp.callback_query(VoiceTranslate.start)
async def generate_image(call: types.CallbackQuery, state: FSMContext):
    if call.data.startswith('language_'):
        lang_code = call.data.split("_")[1]  
        lang_name = next((key for key, value in languages.items() if value == lang_code), lang_code)
        await state.update_data(lang_name=lang_name, lang_code=lang_code)
        await state.set_state(VoiceTranslate.voice)
        await call.message.answer(text=_("Speakerni Tanlng !!!"), reply_markup=voices_button())
    else:
        await call.message.answer(text=_("choose_language"))

@dp.callback_query(VoiceTranslate.voice)
async def get_choose_lang(call: types.CallbackQuery, state: FSMContext):
    if call.data.startswith('voicer_'):
        voicer = call.data.split("_")[1]  
        await state.update_data({'voicer': voicer})
        await state.set_state(VoiceTranslate.middle)
        btn = InlineKeyboardBuilder()
        btn.button(text=_("back_to_main_menu"), callback_data="language_back_button_translate")
        await call.message.answer(text=f'{_("send_voice_message")} \n\n{voicer}', reply_markup=btn.as_markup())
    else:
        await call.message.answer(text=_("Speakerni Tanlng !!!"))
    

@dp.message(VoiceTranslate.middle, MyFilter())
async def get_voice(message: types.Message, state: FSMContext):
    if message.voice:
        data = await state.get_data()
        voicer = data['voicer']
        if 'lang_code' not in data or 'lang_name' not in data:
            await message.answer(text=_("language_not_selected"))
            return
            
        await bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.UPLOAD_VOICE)

        file_id = message.voice.file_id
        file = await bot.get_file(file_id)
        custom_file = f"{BASE_DIR}/media/voice_to_voice/{int(time.time())}.mp3"
        audio = None 
        
        try:
            await bot.download(file=file, destination=custom_file)
            audio, caption = await voice_to_voice_translate(custom_file, data['lang_code'], data['lang_name'], voicer)
            btn = InlineKeyboardBuilder()
            btn.button(text=_("back_to_main_menu"), callback_data="language_back_button_translate")
            btn.button(text=_("change_language_button"), callback_data="change_language_text_1")
            btn.adjust(1)
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
                db.add_chat(user_id=message.chat.id, voice=audio, action="voice",  _state=f'{_("best_ai_bot")} {_("back_to_main_menu_other")}')
                db.delete_all_except_last_chat(message.chat.id)
                return
            await message.answer_audio(audio=FSInputFile(audio), caption=f'{caption} \n\n {_("best_ai_bot")}', reply_markup=btn.as_markup())
            for file_path in [custom_file, audio]:
                if file_path and os.path.exists(file_path):
                    os.remove(file_path)
        except Exception as e:
            await message.answer("Xatolik yuz berdi! Qayta urinib ko'ring.")
            print(f"Xato: {e}")
                        
    elif message.audio:
        data = await state.get_data()
        voicer = data['voicer']
        if 'lang_code' not in data or 'lang_name' not in data:
            await message.answer(text=_("language_not_selected"))
            return
            
        await bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.UPLOAD_VOICE)

        file_id = message.audio.file_id
        file = await bot.get_file(file_id)
        custom_file = f"{BASE_DIR}/media/voice_to_voice/{int(time.time())}.mp3"
        audio = None 
        
        try:
            await bot.download(file=file, destination=custom_file)
            audio, caption = await voice_to_voice_translate(custom_file, data['lang_code'], data['lang_name'], voicer)
            btn = InlineKeyboardBuilder()
            btn.button(text=_("back_to_main_menu"), callback_data="language_back_button_translate")
            btn.button(text=_("change_language_button"), callback_data="change_language_text_1")
            btn.adjust(1)
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
                db.add_chat(user_id=message.chat.id, voice=audio, action="voice")
                db.delete_all_except_last_chat(message.chat.id)
                return
            await message.answer_audio(audio=FSInputFile(audio), caption=f'{caption} \n\n{_("best_ai_bot")}', reply_markup=btn.as_markup())
            for file_path in [custom_file, audio]:
                if file_path and os.path.exists(file_path):
                    os.remove(file_path)
            
        except Exception as e:
            await message.answer("Xatolik yuz berdi! Qayta urinib ko'ring.")
            print(f"Xato: {e}")

    else:
        btn = InlineKeyboardBuilder()
        btn.button(text=_("back_to_main_menu"), callback_data="language_back_button_translate")
        await message.answer(_("send_voice_again"), reply_markup=btn.as_markup())

async def voice_to_voice_translate(audio_path: str, lang_code: str, lang_name: str, voicer) -> str:
    """
    Ovozli faylni tarjima qilish va yangi ovozli fayl yaratish
    
    :param audio_path: Yuklangan ovoz faylining lokal yo'li
    :param lang_code: Tanlangan til kodi (masalan, 'uzbek')
    :param lang_name: Tanlangan tilning to'liq nomi (masalan, 'Uzbek 🇺🇿')
    :return: Yaratilgan yangi ovoz faylining yo'li
    """
    try:
        supported_languages = {
            "en", "es", "fr", "de", "it", "pt", "nl", "ru", "pl", "sv", "tr",
            "hi", "ja", "ko", "zh", "ar", "he", "id", "fi", "cs", "uk", "hu", "ro"
        }             
        # 1. Ovoz faylini transkripsiya qilish (audio -> text)
        with open(audio_path, "rb") as audio_file:
            transcription_params = {
                "model": "whisper-1",
                "file": audio_file,
                "response_format": "text"
            }
            if lang_code in supported_languages:
                transcription_params["language"] = lang_code
            transcription = client.audio.transcriptions.create(**transcription_params)

        translation_prompt = f"Siz tarjimon botsiz. ortiqcha gap yozmang !!!!!!!!!!! matnni {lang_name} tiliga tarjima qiling"
        
        translated_text = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": translation_prompt},
                {"role": "user", "content": transcription}
            ],
            temperature=0.3
        ).choices[0].message.content

       
        tts_response = client.audio.speech.create(
            model="tts-1-hd",
            voice=voicer,  # Tilga qarab ovozni sozlash
            input=translated_text,
            response_format="mp3",
        )

        # 4. Yangi ovoz faylini saqlash
        output_dir = f"{BASE_DIR}/media/voice_to_voice"
        os.makedirs(output_dir, exist_ok=True)  # Papka mavjud emas bo'lsa yaratib olish
        
        output_path = f"{output_dir}/output_{int(time.time())}.mp3"
        tts_response.stream_to_file(output_path)

        return output_path, translated_text

    except Exception as e:
        # Xatoliklarni log qilish
        print(f"Voice translation error: {str(e)}")
        raise  # Xatoni yuqori darajaga uzatish



@dp.callback_query(F.data == "change_language_text_1")
async def change_languages(call: types.CallbackQuery, state: FSMContext, page: int = 0):
    await call.answer(cache_time=60)
    btn = InlineKeyboardBuilder()
    keys = list(languages.keys())
    
    start = page * PER_PAGE
    end = start + PER_PAGE
    current_languages = keys[start:end]

    # Tillarni qo'shish
    for lang in current_languages:
        btn.button(text=lang, callback_data=f"language_{languages[lang]}")
    
    # Navigatsiya tugmalari
    nav_buttons = []
    if page > 0:
        nav_buttons.append(types.InlineKeyboardButton(text=_("previous_button"), callback_data=f"page3_{page - 1}"))
    if end < len(keys):
        nav_buttons.append(types.InlineKeyboardButton(text=_("next_button"), callback_data=f"page3_{page + 1}"))
    
    # Orqaga tugmasi
    nav_buttons.append(types.InlineKeyboardButton(text=_("back_to_main_menu"), callback_data="language_back_button_translate"))

    # Navigatsiya tugmalarini qo'shish
    btn.row(*nav_buttons)  
    btn.adjust(2)  
    await call.message.answer(text=_("choose_translation_language"), reply_markup=btn.as_markup())
    await state.set_state(VoiceTranslate.start)
    















# two translate

    
from states.my_state import  LanguageStateVoice

@dp.callback_query(F.data == "two_translate2")
async def second_send_language_menu(call: types.CallbackQuery, state: FSMContext,  page: int = 0, ):
    await call.answer(cache_time=60)
    btn = InlineKeyboardBuilder()
    keys = list(languages.keys())
    
    start = page * PER_PAGE
    end = start + PER_PAGE
    current_languages = keys[start:end]

    for lang in current_languages:
        btn.button(text=lang, callback_data=f"second_language1_{languages[lang]}")
    
    nav_buttons = []
    if page > 0:
        nav_buttons.append(types.InlineKeyboardButton(text=_("previous_button"), callback_data=f"page_{page - 1}"))
    if end < len(keys):
        nav_buttons.append(types.InlineKeyboardButton(text=_("next_button"), callback_data=f"page_{page + 1}"))
    
    nav_buttons.append(types.InlineKeyboardButton(text=_("back_to_main_menu"), callback_data="language_back_button_translate"))
    btn.row(*nav_buttons)  
    btn.adjust(2)  
    await call.message.answer(text=_("choose_first_language"), reply_markup=btn.as_markup())
    await state.set_state(LanguageStateVoice.first_lang)



# @dp.callback_query(F.data.startswith("page_"))
# async def pagination_handler(call: types.CallbackQuery, state: FSMContext):
#     await call.answer(cache_time=60)
#     page = int(call.data.split("_")[-1])
#     await call.message.edit_text(text=_("choose_first_language"), reply_markup=await get_language_menu(page))
#     await state.set_state(LanguageStateVoice.first_lang)

@dp.callback_query(F.data.startswith("page_"))
async def pagination_handler(call: types.CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    page = int(call.data.split("_")[-1])
    data = await state.get_data()

    if "first_lang_code" not in data:
        await call.message.edit_text(text=_("choose_first_language"), reply_markup=await get_language_menu2(page))
        await state.set_state(LanguageStateVoice.first_lang)
    else:
        await call.message.edit_text(text=_("choose_second_language"), reply_markup=await get_language_menu(page))
        await state.set_state(LanguageStateVoice.second_lang)

async def get_language_menu(page: int):
    btn = InlineKeyboardBuilder()
    keys = list(languages.keys())
    
    start = page * PER_PAGE
    end = start + PER_PAGE
    current_languages = keys[start:end]

    for lang in current_languages:
        btn.button(text=lang, callback_data=f"second_language1_{languages[lang]}")
    
    nav_buttons = []
    if page > 0:
        nav_buttons.append(types.InlineKeyboardButton(text=_("previous_button"), callback_data=f"page_{page - 1}"))
    if end < len(keys):
        nav_buttons.append(types.InlineKeyboardButton(text=_("next_button"), callback_data=f"page_{page + 1}"))
    
    nav_buttons.append(types.InlineKeyboardButton(text=_("back_to_main_menu"), callback_data="language_back_button_translate"))

    btn.row(*nav_buttons)
    btn.adjust(2)

    return btn.as_markup()
async def get_language_menu2(page: int):
    btn = InlineKeyboardBuilder()
    keys = list(languages.keys())

    start = page * PER_PAGE
    end = start + PER_PAGE
    current_languages = keys[start:end]

    for lang in current_languages:
        btn.button(text=lang, callback_data=f"second_language_{languages[lang]}")

    nav_buttons = []
    if page > 0:
        nav_buttons.append(types.InlineKeyboardButton(text=_("previous_button"), callback_data=f"page_{page - 1}"))
    if end < len(keys):
        nav_buttons.append(types.InlineKeyboardButton(text=_("next_button"), callback_data=f"page_{page + 1}"))
    nav_buttons.append(types.InlineKeyboardButton(text=_("back_to_main_menu"), callback_data="language_back_button_translate"))

    btn.row(*nav_buttons)
    btn.adjust(2)

    return btn.as_markup()



@dp.callback_query(lambda query: query.data.startswith('second_language1_'), LanguageStateVoice.first_lang)
async def get_first_lang(call: types.CallbackQuery, state: FSMContext, page: int = 0):
    await call.answer(cache_time=60)
    lang_code = call.data.split("_")[-1]  
    lang_name = next((key for key, value in languages.items() if value == lang_code), lang_code)  
    await state.update_data({"first_lang_code": lang_code, "first_lang_name": lang_name})
    await call.answer(cache_time=60)
    btn = InlineKeyboardBuilder()
    keys = list(languages.keys())
    
    start = page * PER_PAGE
    end = start + PER_PAGE
    current_languages = keys[start:end]

    for lang in current_languages:
        btn.button(text=lang, callback_data=f"second_2language1_{languages[lang]}")
    
    nav_buttons = []
    if page > 0:
        nav_buttons.append(types.InlineKeyboardButton(text=_("previous_button"), callback_data=f"page_{page - 1}"))
    if end < len(keys):
        nav_buttons.append(types.InlineKeyboardButton(text=_("next_button"), callback_data=f"page_{page + 1}"))
    
    nav_buttons.append(types.InlineKeyboardButton(text=_("back_to_main_menu"), callback_data="language_back_button_translate"))


    btn.row(*nav_buttons)  
    btn.adjust(2)  
    await call.message.answer(text=_("choose_second_language"), reply_markup=btn.as_markup())
    await state.set_state(LanguageStateVoice.second_lang)
    return



# @dp.callback_query(F.data.startswith("page_"))
# async def pagination_handler(call: types.CallbackQuery, state: FSMContext):
#     await call.answer(cache_time=60)
#     page = int(call.data.split("_")[-1])
#     await call.message.edit_text(text=_("choose_second_language"), reply_markup=await get_language_menu(page))
#     await state.set_state(LanguageStateVoice.second_lang)

async def get_language_menu(page: int):
    btn = InlineKeyboardBuilder()
    keys = list(languages.keys())
    
    start = page * PER_PAGE
    end = start + PER_PAGE
    current_languages = keys[start:end]

    for lang in current_languages:
        btn.button(text=lang, callback_data=f"second_2language1_{languages[lang]}")
    
    nav_buttons = []
    if page > 0:
        nav_buttons.append(types.InlineKeyboardButton(text=_("previous_button"), callback_data=f"page_{page - 1}"))
    if end < len(keys):
        nav_buttons.append(types.InlineKeyboardButton(text=_("next_button"), callback_data=f"page_{page + 1}"))
    
    nav_buttons.append(types.InlineKeyboardButton(text=_("back_to_main_menu"), callback_data="language_back_button_translate"))

    btn.row(*nav_buttons)
    btn.adjust(2)

    return btn.as_markup()


@dp.callback_query(lambda query:query.data.startswith('second_2language1_'), LanguageStateVoice.second_lang)
async def get_first_lang(call: types.CallbackQuery, state: FSMContext):
        await call.answer(cache_time=60)
        lang_code = call.data.split("_")[-1]  
        lang_name = next((key for key, value in languages.items() if value == lang_code), lang_code)  
        await state.update_data({"second_lang_code": lang_code, "second_lang_name": lang_name})
        data = await state.get_data()
        first_lang_name = data["first_lang_name"]
        
        btn = InlineKeyboardBuilder()
        btn.button(text=f"{first_lang_name} {lang_name}", callback_data="change_language")
        await call.message.answer(
        text=_("Speakerni Tanlng !!!"), 
        # text=_("send_voice_message") + f"\n\n{text}", 

        reply_markup=voices_button()
    )
        await state.set_state(LanguageStateVoice.text)

@dp.callback_query(LanguageStateVoice.text)
async def get_voicer(call: types.CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    voicer = call.data.split("_")[-1]
    await state.update_data({'voicer': voicer})
    await state.set_state(LanguageStateVoice.voice)
    btn = InlineKeyboardBuilder()
    btn.button(text=_("back_to_main_menu"), callback_data="main_menu_back")
    data = await state.get_data()
    first_lang_name = data['first_lang_name']
    second_lang_name = data['second_lang_name']
    await call.message.answer(text=f'{_("send_voice_message")} \n\n{first_lang_name} {second_lang_name}', reply_markup=btn.as_markup())

    # await call.message.answer(text=f'{_("send_text"),} \n\n{voicer}', reply_markup=btn.as_markup())
    # await state.set_state(Text_To_Voice.voice)

@dp.message(LanguageStateVoice.voice, MyFilter())
async def get_datas(message: types.Message, state: FSMContext):
    data = await state.get_data()
    voicer = data['voicer']
    if message.voice:        
        await bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.UPLOAD_VOICE)

        file_id = message.voice.file_id
        file = await bot.get_file(file_id)
        custom_file = f"{BASE_DIR}/media/voice_to_voice/{int(time.time())}.mp3"
        audio = None 
        
        try:
            await bot.download(file=file, destination=custom_file)
            first_lang = data["first_lang_name"]
            second_lang = data["second_lang_name"]
            first_lang_code = data["first_lang_code"]
            second_lang_code = data["second_lang_code"]
            audio, caption = await voice_to_voice_translate1(custom_file, first_lang, second_lang, first_lang_code, second_lang_code, voicer)
            btn = InlineKeyboardBuilder()
            btn.button(text=_("back_to_main_menu"), callback_data="language_back_button_translate")
            btn.button(text=f"{first_lang} {second_lang}", callback_data="change_language")
            btn.button(text=_("change_language_button"), callback_data="change_language_text1000")
            btn.adjust(1)
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
                db.add_chat(user_id=message.chat.id, voice=audio, action="voice", _state=f'{_("best_ai_bot")} {_("back_to_main_menu_other")}')
                db.delete_all_except_last_chat(message.chat.id)
                return
            await message.answer_audio(audio=FSInputFile(audio), caption=f'{caption} \n\n{_("best_ai_bot")}', reply_markup=btn.as_markup())
            for file_path in [custom_file, audio]:
                if file_path and os.path.exists(file_path):
                    os.remove(file_path)
            
        except Exception as e:
            await message.answer("Xatolik yuz berdi! Qayta urinib ko'ring.")
            print(f"Xato: {e}")
    
            
                    
    elif message.audio:
        await bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.UPLOAD_VOICE)
        file_id = message.audio.file_id
        file = await bot.get_file(file_id)
        custom_file = f"{BASE_DIR}/media/voice_to_voice/{int(time.time())}.mp3"
        audio = None 
        
        try:
            await bot.download(file=file, destination=custom_file)
            first_lang = data["first_lang_name"]
            second_lang = data["second_lang_name"]
            first_lang_code = data["first_lang_code"]
            second_lang_code = data["second_lang_code"]
            audio, caption = await voice_to_voice_translate1(custom_file, first_lang, second_lang, first_lang_code, second_lang_code, voicer)
            btn = InlineKeyboardBuilder()
            btn.button(text=_("back_to_main_menu"), callback_data="language_back_button_translate")
            btn.button(text=f"{first_lang} {second_lang}", callback_data="change_language")
            btn.button(text=_("change_language_button"), callback_data="change_language_text1000")
            btn.adjust(1)
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
                db.add_chat(user_id=message.chat.id, voice=audio, action="voice", _state=f'{_("best_ai_bot")} {_("back_to_main_menu_other")}')
                db.delete_all_except_last_chat(message.chat.id)
                return
            await message.answer_audio(audio=FSInputFile(audio), caption=f'{caption} \n\n{_("best_ai_bot")}', reply_markup=btn.as_markup())
            for file_path in [custom_file, audio]:
                if file_path and os.path.exists(file_path):
                    os.remove(file_path)
            
        except Exception as e:
            await message.answer("Xatolik yuz berdi! Qayta urinib ko'ring.")
            print(f"Xato: {e}")
            
            
    else:
        btn  =InlineKeyboardBuilder()
        btn.button(text=_("back_to_main_menu"), callback_data="language_back_button_translate")
        await message.answer(_("send_voice_or_audio_message"), reply_markup=btn.as_markup())



@dp.callback_query(F.data == "change_language")
async def change_lang(call: types.CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    data = await state.get_data()
    first_lang_code = data["first_lang_code"]
    second_lang_code = data["second_lang_code"]
    first_lang_name = data["first_lang_name"]
    second_lang_name = data["second_lang_name"]
    text = f"{second_lang_name} {first_lang_name}"
    await state.update_data({"first_lang_code": second_lang_code, "second_lang_code": first_lang_code, "first_lang_name": second_lang_name, "second_lang_name": first_lang_name})
    data = await state.get_data()
    btn = InlineKeyboardBuilder()
    btn.button(text=f'{data["first_lang_name"]} {data["second_lang_name"]}', callback_data="change_language")
    await call.message.answer(
    text=_("send_voice_message") + f"\n\n{text}", 
    reply_markup=btn.as_markup()
)



@dp.callback_query(F.data == "change_language_text1000")
async def change_languages(call: types.CallbackQuery, state: FSMContext, page: int = 0):
    await call.answer(cache_time=60)
    btn = InlineKeyboardBuilder()
    keys = list(languages.keys())
    
    start = page * PER_PAGE
    end = start + PER_PAGE
    current_languages = keys[start:end]

    for lang in current_languages:
        btn.button(text=lang, callback_data=f"second_language1_{languages[lang]}")
    
    nav_buttons = []
    if page > 0:
        nav_buttons.append(types.InlineKeyboardButton(text=_("previous_button"), callback_data=f"page_{page - 1}"))
    if end < len(keys):
        nav_buttons.append(types.InlineKeyboardButton(text=_("next_button"), callback_data=f"page_{page + 1}"))
    
    nav_buttons.append(types.InlineKeyboardButton(text=_("back_to_main_menu"), callback_data="language_back_button_translate"))
    btn.row(*nav_buttons)  
    btn.adjust(2)  
    await call.message.answer(text=_("choose_first_language"), reply_markup=btn.as_markup())
    await state.set_state(LanguageStateVoice.first_lang)


async def voice_to_voice_translate1(audio_path: str, lang_name_first: str, lang_name_second: str, first_lang_code: str, second_lang_code: str, vocier):
    """
    Ovozli faylni tarjima qilish va yangi ovozli fayl yaratish.
    
    :param audio_path: Yuklangan ovoz faylining lokal yo'li
    :param lang_name_first: Birinchi til nomi (masalan, 'Uzbek')
    :param lang_name_second: Ikkinchi til nomi (masalan, 'Russian')
    :return: Yaratilgan yangi ovoz faylining yo'li va tarjima matni
    """
    try:
        supported_languages = {
            "en", "es", "fr", "de", "it", "pt", "nl", "ru", "pl", "sv", "tr",
            "hi", "ja", "ko", "zh", "ar", "he", "id", "fi", "cs", "uk", "hu", "ro"
        }
        print(second_lang_code)
        with open(audio_path, "rb") as audio_file:
            transcription_params = {
                "model": "whisper-1",
                "file": audio_file,
                "response_format": "text",
                
            }
            if second_lang_code in supported_languages:
                transcription_params["language"] = second_lang_code  

            transcription = client.audio.transcriptions.create(**transcription_params)

        print(f"Transkripsiya: {transcription}")

        translation_prompt = f"Quyidagi matnni {lang_name_second} tiliga aniq tarjima qiling."

        translated_text = client.chat.completions.create(
            model="chatgpt-4o-latest",
            messages=[
                {"role": "system", "content": translation_prompt},
                {"role": "user", "content": transcription}
            ],
            temperature=0.3
        ).choices[0].message.content
        print(f"Tarjima matn: {translated_text}")

        tts_response = client.audio.speech.create(
            model="tts-1-hd",
            voice=vocier,
            input=translated_text,
            response_format="mp3"
        )

        # 6. Faylni saqlash
        output_dir = BASE_DIR / "media/voice_to_voice"
        os.makedirs(output_dir, exist_ok=True)
        
        output_path = output_dir / f"output_{int(time.time())}.mp3"
        tts_response.stream_to_file(output_path)

        return str(output_path), transcription

    except Exception as e:
        print(f"Xatolik: {str(e)}")
        raise