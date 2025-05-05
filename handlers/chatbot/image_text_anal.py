from aiogram.fsm.context import FSMContext
from loader import dp, db
from aiogram import types, F
from data.config import OPENAI_KEY, BOT_TOKEN
from openai import OpenAI
from loader import bot
from aiogram.enums.chat_action import ChatAction
from states.my_state import Image_Text_Translate
from filters.my_filter import MyFilter
from handlers.channels.fetch_count import is_fetch_limit_reached
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types.web_app_info import WebAppInfo
from data.config import MINI_APP_URL
import asyncio
from handlers.webapp.app import random_webapp_url
from keyboards.default.button import voices_button
from aiogram.utils.i18n import gettext as _


client = OpenAI(api_key=OPENAI_KEY)


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

async def analyze_image(image_url, caption: str = None, lang_name: str = None):
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"Rasmdagi textni olib ber"},
                    {"type": "image_url", "image_url":  {"url": f"{image_url}", "detail": "low"}},
                ],
            }
        ],
    )
    translation_prompt = f"Quyidagi matnni {lang_name} tiliga aniq tarjima qiling."
    translated_text = client.chat.completions.create(
        model="chatgpt-4o-latest",
        messages=[
            {"role": "system", "content": translation_prompt},
            {"role": "user", "content": response.choices[0].message.content}
        ],
        temperature=0.3
    ).choices[0].message.content
    return translated_text



@dp.callback_query(F.data == "image_translate_")
async def start_image(call: types.CallbackQuery, state: FSMContext, page: int = 0):
    await call.answer(cache_time=60)
    btn = InlineKeyboardBuilder()
    keys = list(languages.keys())
    
    start = page * PER_PAGE
    end = start + PER_PAGE
    current_languages = keys[start:end]

    # Tillarni qo'shish
    for lang in current_languages:
        btn.button(text=lang, callback_data=f"language7_{languages[lang]}")
    
    # Navigatsiya tugmalari
    nav_buttons = []
    if page > 0:
        nav_buttons.append(types.InlineKeyboardButton(text=_("previous_button"), callback_data=f"page7_{page - 1}"))
    if end < len(keys):
        nav_buttons.append(types.InlineKeyboardButton(text=_("next_button"), callback_data=f"page7_{page + 1}"))
    
    # Orqaga tugmasi
    nav_buttons.append(types.InlineKeyboardButton(text=_("back_to_main_menu"), callback_data="language_back_button_translate"))

    # Navigatsiya tugmalarini qo'shish
    btn.row(*nav_buttons)  
    btn.adjust(2)  
    await call.message.answer(text=_("choose_translation_language"), reply_markup=btn.as_markup())
    await state.set_state(Image_Text_Translate.start)
    

@dp.callback_query(F.data.startswith("page7_"))
async def pagination_handler(call: types.CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    page = int(call.data.split("_")[1])
    await call.message.edit_text(text=_("choose_translation_language"), reply_markup=await get_language_menu3(page))
    await state.set_state(Image_Text_Translate.start)

async def get_language_menu3(page: int):
    btn = InlineKeyboardBuilder()
    keys = list(languages.keys())
    
    start = page * PER_PAGE
    end = start + PER_PAGE
    current_languages = keys[start:end]

    for lang in current_languages:
        btn.button(text=lang, callback_data=f"language7_{languages[lang]}")
    
    nav_buttons = []
    if page > 0:
        nav_buttons.append(types.InlineKeyboardButton(text=_("previous_button"), callback_data=f"page7_{page - 1}"))
    if end < len(keys):
        nav_buttons.append(types.InlineKeyboardButton(text=_("next_button"), callback_data=f"page7_{page + 1}"))
    
    # Orqaga tugmasi
    nav_buttons.append(types.InlineKeyboardButton(text=_("back_to_main_menu"), callback_data="language_back_button_translate"))

    btn.row(*nav_buttons)
    btn.adjust(2)

    return btn.as_markup()


@dp.callback_query(Image_Text_Translate.start, F.data.startswith('language7_'))
async def get_(call: types.CallbackQuery, state: FSMContext):
    lang_code = call.data.split("_")[1]  
    lang_name = next((key for key, value in languages.items() if value == lang_code), lang_code)
    print(lang_code, lang_name)
    await state.update_data(lang_name=lang_name, lang_code=lang_code)
    btn = InlineKeyboardBuilder()
    btn.button(text=_("back_to_main_menu"), callback_data="main_menu_back")
    await call.answer(cache_time=60)
    await call.message.answer(text=_("send_image"), reply_markup=btn.as_markup())
    await state.set_state(Image_Text_Translate.lang)

@dp.message(Image_Text_Translate.lang, MyFilter())
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
        data = await state.get_data()
        analysis_result = await analyze_image(photo_url, caption, data['lang_name'])
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
        #     db.add_chat(user_id=message.chat.id, image=message.photo[-1].file_id, action="image",  _text=analysis_result, _state=f'{_("best_ai_bot")} {_("back_to_main_menu_other")}')
        #     db.delete_all_except_last_chat(message.chat.id)
        #     await state.set_state(Image_Text_Translate.start)
        #     return
        await message.reply(f'{analysis_result} \n\n{_("best_ai_bot")}', reply_markup=button.as_markup())
        await state.set_state(Image_Text_Translate.start)
        await info.delete()
        return
    else:
        await message.answer(text=_("please_send_image"), reply_markup=button.as_markup())
