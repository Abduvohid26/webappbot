from aiogram.fsm.context import FSMContext
from loader import dp, db
from aiogram import types, F
from data.config import OPENAI_KEY
from openai import OpenAI
from loader import bot
from states.my_state import TranslateState
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


client = OpenAI(
    api_key=OPENAI_KEY
)


@dp.callback_query(F.data == 'language_back_button_translate')
async def back_button(call: types.CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    await state.clear()
    await call.message.answer(text=_("main_menu"), reply_markup=menu_button())

async def translate_text(user_prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Xatolik yuz berdi: {str(e)}"




languages = {
    # Turk tillari
    "Uzbek 🇺🇿": "uzbek",
    "Turkish 🇹🇷": "turkish",
    "Kazakh 🇰🇿": "kazakh",
    "Azerbaijani 🇦🇿": "azerbaijani",
    "Turkmen 🇹🇲": "turkmen",
    "Tatar 🇷🇺": "tatar",
    "Kyrgyz 🇰🇬": "kyrgyz",
    "Uighur 🇨🇳": "uighur",
    
    # Yevropa tillari
    "English 🇬🇧": "english",
    "Russian 🇷🇺": "russian",
    "French 🇫🇷": "french",
    "German 🇩🇪": "german",
    "Spanish 🇪🇸": "spanish",
    "Italian 🇮🇹": "italian",
    "Portuguese 🇵🇹": "portuguese",
    "Dutch 🇳🇱": "dutch",
    "Polish 🇵🇱": "polish",
    "Ukrainian 🇺🇦": "ukrainian",
    "Greek 🇬🇷": "greek",
    "Swedish 🇸🇪": "swedish",
    "Finnish 🇫🇮": "finnish",
    "Danish 🇩🇰": "danish",
    "Norwegian 🇳🇴": "norwegian",
    "Hungarian 🇭🇺": "hungarian",
    "Czech 🇨🇿": "czech",
    "Slovak 🇸🇰": "slovak",
    "Romanian 🇷🇴": "romanian",
    "Serbian 🇷🇸": "serbian",
    "Croatian 🇭🇷": "croatian",
    "Bulgarian 🇧🇬": "bulgarian",
    "Albanian 🇦🇱": "albanian",
    "Lithuanian 🇱🇹": "lithuanian",
    "Latvian 🇱🇻": "latvian",
    "Estonian 🇪🇪": "estonian",
    "Belarusian 🇧🇾": "belarusian",
    "Basque 🇪🇸": "basque",
    "Catalan 🇪🇸": "catalan",
    "Irish 🇮🇪": "irish",
    "Scottish Gaelic 🏴": "scottish_gaelic",
    "Welsh 🏴": "welsh",
    
    # Osiyo tillari
    "Chinese 🇨🇳": "chinese",
    "Japanese 🇯🇵": "japanese",
    "Korean 🇰🇷": "korean",
    "Mongolian 🇲🇳": "mongolian",
    "Tajik 🇹🇯": "tajik",
    "Hindi 🇮🇳": "hindi",
    "Bengali 🇧🇩": "bengali",
    "Urdu 🇵🇰": "urdu",
    "Persian 🇮🇷": "persian",
    "Pashto 🇦🇫": "pashto",
    "Punjabi 🇮🇳": "punjabi",
    "Tamil 🇮🇳": "tamil",
    "Telugu 🇮🇳": "telugu",
    "Marathi 🇮🇳": "marathi",
    "Gujarati 🇮🇳": "gujarati",
    "Malayalam 🇮🇳": "malayalam",
    "Kannada 🇮🇳": "kannada",
    "Sinhala 🇱🇰": "sinhala",
    "Nepali 🇳🇵": "nepali",
    "Thai 🇹🇭": "thai",
    "Lao 🇱🇦": "lao",
    "Burmese 🇲🇲": "burmese",
    "Khmer 🇰🇭": "khmer",
    "Vietnamese 🇻🇳": "vietnamese",
    "Malay 🇲🇾": "malay",
    "Indonesian 🇮🇩": "indonesian",
    "Filipino 🇵🇭": "filipino",
    "Hebrew 🇮🇱": "hebrew",
    "Georgian 🇬🇪": "georgian",
    "Armenian 🇦🇲": "armenian",
    
    # Arab va Afrika tillari
    "Arabic 🇸🇦": "arabic",
    "Swahili 🇰🇪": "swahili",
    "Amharic 🇪🇹": "amharic",
    "Hausa 🇳🇬": "hausa",
    "Yoruba 🇳🇬": "yoruba",
    "Igbo 🇳🇬": "igbo",
    "Zulu 🇿🇦": "zulu",
    "Xhosa 🇿🇦": "xhosa",
    "Afrikaans 🇿🇦": "afrikaans",
    "Somali 🇸🇴": "somali",
    "Berber 🇲🇦": "berber",
    
    # Amerika va Okeaniya tillari
    "Hawaiian 🇺🇸": "hawaiian",
    "Maori 🇳🇿": "maori",
    "Samoan 🇼🇸": "samoan",
    "Tongan 🇹🇴": "tongan",
    "Quechua 🇵🇪": "quechua",
    "Aymara 🇧🇴": "aymara",
    "Guarani 🇵🇾": "guarani",
    
    # Sun'iy va maxsus tillar
    "Esperanto 🌍": "esperanto",
    "Latin 🇻🇦": "latin",
    "↩️ Orqaga": "back_button_translate"
}

PER_PAGE = 10

@dp.callback_query(F.data == "translater_bot")
async def start_lang_(call: types.CallbackQuery):
    btn = InlineKeyboardBuilder()
    btn.button(text="📝 Translater V1", callback_data="one_translate")
    btn.button(text="📝 Translater V2", callback_data="two_translate")
    btn.adjust(1)
    await call.message.answer(text=_("choose_option"), reply_markup=btn.as_markup())



@dp.callback_query(F.data == "one_translate")
async def send_language_menu(call: types.CallbackQuery, state: FSMContext,  page: int = 0, ):
    await call.answer(cache_time=60)
    btn = InlineKeyboardBuilder()
    keys = list(languages.keys())
    
    start = page * PER_PAGE
    end = start + PER_PAGE
    current_languages = keys[start:end]

    for lang in current_languages:
        btn.button(text=lang, callback_data=f"language_{languages[lang]}")
    
    nav_buttons = []
    if page > 0:
        nav_buttons.append(types.InlineKeyboardButton(text=_("previous_button"), callback_data=f"page1_{page - 1}"))
    if end < len(keys):
        nav_buttons.append(types.InlineKeyboardButton(text=_("next_button"), callback_data=f"page1_{page + 1}"))
    
    nav_buttons.append(types.InlineKeyboardButton(text=_("back_to_main_menu"), callback_data="language_back_button_translate"))

    btn.row(*nav_buttons)  
    btn.adjust(2)  
    await call.message.answer(text=_("choose_translation_language"), reply_markup=btn.as_markup())
    await state.set_state(TranslateState.start)



@dp.callback_query(F.data.startswith("page1_"))
async def pagination_handler(call: types.CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    page = int(call.data.split("_")[1])
    await call.message.edit_text(text=_("choose_translation_language"), reply_markup=await get_language_menu1(page))
    await state.set_state(TranslateState.start)

async def get_language_menu1(page: int):
    btn = InlineKeyboardBuilder()
    keys = list(languages.keys())
    
    start = page * PER_PAGE
    end = start + PER_PAGE
    current_languages = keys[start:end]

    for lang in current_languages:
        btn.button(text=lang, callback_data=f"language_{languages[lang]}")
    
    nav_buttons = []
    if page > 0:
        nav_buttons.append(types.InlineKeyboardButton(text=_("previous_button"), callback_data=f"page1_{page - 1}"))
    if end < len(keys):
        nav_buttons.append(types.InlineKeyboardButton(text=_("next_button"), callback_data=f"page1_{page + 1}"))
    nav_buttons.append(types.InlineKeyboardButton(text=_("back_to_main_menu"), callback_data="language_back_button_translate"))

    btn.row(*nav_buttons)
    btn.adjust(2)

    return btn.as_markup()

@dp.callback_query(TranslateState.start)
async def select_language(call: types.CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    print(call.data, 'data')
    if call.data.startswith('language_'):
        lang_code = call.data.split("_")[1]  
        lang_name = next((key for key, value in languages.items() if value == lang_code), lang_code)  

        await state.update_data(lang=lang_code)  

        await call.answer(cache_time=60)
        btn  = InlineKeyboardBuilder()
        btn.button(text="↩️ Orqaga", callback_data="language_back_button_translate")
        await call.message.answer(_("send_text_for_translation").format(lang_name=lang_name), reply_markup=btn.as_markup())
        await state.set_state(TranslateState.finish)
        return
    btn = InlineKeyboardBuilder()
    
    for lang, code in languages.items():
        btn.button(text=lang, callback_data=f'language_{code}')

    btn.adjust(2)
    await call.message.answer(text=_("please_choose_language"), reply_markup=btn.as_markup())

@dp.message(TranslateState.finish, MyFilter())
async def translate_message(message: types.Message, state: FSMContext):
    btn  = InlineKeyboardBuilder()
    btn.button(text=_("back_to_main_menu"), callback_data="language_back_button_translate")
    btn.button(text=_("change_language_button"), callback_data="change_language_text1")
    btn.adjust(1)
    if message.text:
        data = await state.get_data()
        lang = data.get("lang", "english") 
        lang_name = next((key for key, value in languages.items() if value == lang), lang)  
        user_text = message.text

        translated_text_ = await translate_text(f"Quyidagi matnni {lang} tiliga tarjima qil: \n\n{user_text}")
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
        #     db.add_chat(user_id=message.chat.id, _text=translated_text_, action="translate1")
        #     db.delete_all_except_last_chat(message.chat.id)
        #     return
        await message.answer(f'({lang_name}):\n{translated_text_} \n\n{_("best_ai_bot")}', reply_markup=btn.as_markup())

        return
    await message.answer(text=_("send_text_to_translate"))
    



@dp.callback_query(F.data == "change_language_text1")
async def change_language1(call: types.CallbackQuery, state: FSMContext, page: int = 0):
    await call.answer(cache_time=60)
    btn = InlineKeyboardBuilder()
    keys = list(languages.keys())
    
    start = page * PER_PAGE
    end = start + PER_PAGE
    current_languages = keys[start:end]

    for lang in current_languages:
        btn.button(text=lang, callback_data=f"language_{languages[lang]}")
    
    nav_buttons = []
    if page > 0:
        nav_buttons.append(types.InlineKeyboardButton(text=_("previous_button"), callback_data=f"page1_{page - 1}"))
    if end < len(keys):
        nav_buttons.append(types.InlineKeyboardButton(text=_("next_button"), callback_data=f"page1_{page + 1}"))
    
    nav_buttons.append(types.InlineKeyboardButton(text=_("back_to_main_menu"), callback_data="language_back_button_translate"))

    btn.row(*nav_buttons)  
    btn.adjust(2)  
    await call.message.answer(text=_("choose_translation_language"), reply_markup=btn.as_markup())
    await state.set_state(TranslateState.start)






















# two translate






    
from states.my_state import LanguageState

@dp.callback_query(F.data == "two_translate")
async def second_send_language_menu(call: types.CallbackQuery, state: FSMContext,  page: int = 0, ):
    await call.answer(cache_time=60)
    btn = InlineKeyboardBuilder()
    keys = list(languages.keys())
    
    start = page * PER_PAGE
    end = start + PER_PAGE
    current_languages = keys[start:end]

    for lang in current_languages:
        btn.button(text=lang, callback_data=f"second_language_{languages[lang]}")
    
    nav_buttons = []
    if page > 0:
        nav_buttons.append(types.InlineKeyboardButton(text=_("previous_button"), callback_data=f"page2_{page - 1}"))
    if end < len(keys):
        nav_buttons.append(types.InlineKeyboardButton(text=_("next_button"), callback_data=f"page2_{page + 1}"))
    
    nav_buttons.append(types.InlineKeyboardButton(text=_("back_to_main_menu"), callback_data="language_back_button_translate"))
    btn.row(*nav_buttons)  
    btn.adjust(2)  
    await call.message.answer(text=_("choose_first_language"), reply_markup=btn.as_markup())
    await state.set_state(LanguageState.first_lang)



# @dp.callback_query(F.data.startswith("page2_"))
# async def pagination_handler(call: types.CallbackQuery, state: FSMContext):
#     await call.answer(cache_time=60)
#     page = int(call.data.split("_")[-1])
#     await call.message.edit_text(text=_("please_choose_language"), reply_markup=await get_language_menu2(page))
#     await state.set_state(LanguageState.first_lang)

@dp.callback_query(F.data.startswith("page2_"))
async def pagination_handler(call: types.CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    page = int(call.data.split("_")[-1])
    data = await state.get_data()

    if "first_lang_code" not in data:
        await call.message.edit_text(text=_("choose_first_language"), reply_markup=await get_language_menu2(page))
        await state.set_state(LanguageState.first_lang)
    else:
        await call.message.edit_text(text=_("choose_second_language"), reply_markup=await get_language_menu(page))
        await state.set_state(LanguageState.second_lang)

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
        nav_buttons.append(types.InlineKeyboardButton(text=_("previous_button"), callback_data=f"page2_{page - 1}"))
    if end < len(keys):
        nav_buttons.append(types.InlineKeyboardButton(text=_("next_button"), callback_data=f"page2_{page + 1}"))
    nav_buttons.append(types.InlineKeyboardButton(text=_("back_to_main_menu"), callback_data="language_back_button_translate"))

    btn.row(*nav_buttons)
    btn.adjust(2)

    return btn.as_markup()
# async def get_language_menu2(page: int):
#     btn = InlineKeyboardBuilder()
#     keys = list(languages.keys())
    
#     start = page * PER_PAGE
#     end = start + PER_PAGE
#     current_languages = keys[start:end]

#     for lang in current_languages:
#         btn.button(text=lang, callback_data=f"second_language_{languages[lang]}")
    
#     nav_buttons = []
#     if page > 0:
#         nav_buttons.append(types.InlineKeyboardButton(text=_("previous_button"), callback_data=f"page2_{page - 1}"))
#     if end < len(keys):
#         nav_buttons.append(types.InlineKeyboardButton(text=_("next_button"), callback_data=f"page2_{page + 1}"))
#     nav_buttons.append(types.InlineKeyboardButton(text=_("back_to_main_menu"), callback_data="language_back_button_translate"))

#     btn.row(*nav_buttons)
#     btn.adjust(2)

#     return btn.as_markup()


@dp.callback_query(LanguageState.first_lang)
async def get_first_lang(call: types.CallbackQuery, state: FSMContext, page: int = 0):
    await call.answer(cache_time=60)
    if call.data.startswith('second_language_'):
        print(call.data)
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
            btn.button(text=lang, callback_data=f"second_2language_{languages[lang]}")
        
        nav_buttons = []
        if page > 0:
            nav_buttons.append(types.InlineKeyboardButton(text=_("previous_button"), callback_data=f"page2_{page - 1}"))
        if end < len(keys):
            nav_buttons.append(types.InlineKeyboardButton(text=_("next_button"), callback_data=f"page2_{page + 1}"))
        
        nav_buttons.append(types.InlineKeyboardButton(text=_("back_to_main_menu"), callback_data="language_back_button_translate"))


        btn.row(*nav_buttons)  
        btn.adjust(2)  
        await call.message.answer(_("choose_second_language"), reply_markup=btn.as_markup())
        await state.set_state(LanguageState.second_lang)
        return
    await call.message.answer(text=_("please_choose_language"))



# @dp.callback_query(F.data.startswith("page2_"))
# async def pagination_handler(call: types.CallbackQuery, state: FSMContext):
#     await call.answer(cache_time=60)
#     page = int(call.data.split("_")[-1])
#     await call.message.edit_text(text=_("choose_second_language"), reply_markup=await get_language_menu(page))
#     await state.set_state(LanguageState.second_lang)

async def get_language_menu(page: int):
    btn = InlineKeyboardBuilder()
    keys = list(languages.keys())

    start = page * PER_PAGE
    end = start + PER_PAGE
    current_languages = keys[start:end]

    for lang in current_languages:
        btn.button(text=lang, callback_data=f"second_2language_{languages[lang]}")

    nav_buttons = []
    if page > 0:
        nav_buttons.append(types.InlineKeyboardButton(text=_("previous_button"), callback_data=f"page2_{page - 1}"))
    if end < len(keys):
        nav_buttons.append(types.InlineKeyboardButton(text=_("next_button"), callback_data=f"page2_{page + 1}"))
    nav_buttons.append(types.InlineKeyboardButton(text=_("back_to_main_menu"), callback_data="language_back_button_translate"))

    btn.row(*nav_buttons)
    btn.adjust(2)

    return btn.as_markup()


@dp.callback_query(lambda query:query.data.startswith('second_2language_'), LanguageState.second_lang)
async def get_first_lang(call: types.CallbackQuery, state: FSMContext):
        await call.answer(cache_time=60)
        lang_code = call.data.split("_")[-1]  
        lang_name = next((key for key, value in languages.items() if value == lang_code), lang_code)  
        await state.update_data({"second_lang_code": lang_code, "second_lang_name": lang_name})
        data = await state.get_data()
        first_lang = data["first_lang_name"]
        await call.message.answer(text=_(f"Now send me the text\n\n{first_lang}  {lang_name}"))

        await state.set_state(LanguageState.text)



@dp.message(LanguageState.text)
async def get_datas(msg: types.Message, state: FSMContext):
    await bot.send_chat_action(chat_id=msg.chat.id, action=ChatAction.TYPING)
    data = await state.get_data()
    first_lang = data["first_lang_name"]
    second_lang = data["second_lang_name"]
    res =  await translated_text_(text=msg.text, lang_name_first=first_lang, lang_name_second=second_lang)
    btn = InlineKeyboardBuilder()
    btn.button(text=_("back_to_main_menu"), callback_data="language_back_button_translate")
    btn.button(text=_("change_language_button"), callback_data="change_language_text")
    btn.adjust(1)
    # check = is_fetch_limit_reached(msg.from_user.id)
    # if not check:
    data = db.get_user_fetch_count_new(user_id=msg.from_user.id)
    if data[0] == 0:
        webapp_url = await random_webapp_url(msg.from_user.id)
        # btn = InlineKeyboardBuilder()
        # btn.button(text=_("get_answer_button"), web_app=WebAppInfo(url=webapp_url))
        # await msg.answer(text=_("press_button_to_get_answer"), reply_markup=btn.as_markup())
        btn = InlineKeyboardBuilder()
        btn.button(text=_("👥 Do'st taklif qilish"), callback_data="referal_offer")
        btn.button(text=_("back_to_main_menu"), callback_data="back_to_main_menu_other")
        btn.adjust(1)
        await msg.answer(text=_("Bepul limit olish uchun dostingiz taklif qiling"), reply_markup=btn.as_markup())
        db.update_user_fetch_new(user_id=msg.chat.id)
        db.add_chat(user_id=msg.chat.id, _text=res, action="translate2",   _state=f'{_("best_ai_bot")} {_("back_to_main_menu_other")}')
        db.delete_all_except_last_chat(msg.chat.id)
        await state.set_state(LanguageState.text)
        return
    await msg.answer(text=f'{res} \n\n{_("best_ai_bot")}', reply_markup=btn.as_markup())
    await state.set_state(LanguageState.text)



async def translated_text_(text, lang_name_first, lang_name_second):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": f"Siz tarjimon botsiz. Agar matn '{lang_name_first}' tilida bo'lsa, uni '{lang_name_second}' tiliga tarjima qiling. Aks holda, aksincha tarjima qiling."},
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message.content

@dp.callback_query(F.data == "change_language_text")
async def change_languages(call: types.CallbackQuery, state: FSMContext, page: int = 0):
    await call.answer(cache_time=60)
    btn = InlineKeyboardBuilder()
    keys = list(languages.keys())
    
    start = page * PER_PAGE
    end = start + PER_PAGE
    current_languages = keys[start:end]

    for lang in current_languages:
        btn.button(text=lang, callback_data=f"second_language_{languages[lang]}")
    
    nav_buttons = []
    if page > 0:
        nav_buttons.append(types.InlineKeyboardButton(text=_("previous_button"), callback_data=f"page2_{page - 1}"))
    if end < len(keys):
        nav_buttons.append(types.InlineKeyboardButton(text=_("next_button"), callback_data=f"page2_{page + 1}"))
    
    nav_buttons.append(types.InlineKeyboardButton(text=_("back_to_main_menu"), callback_data="language_back_button_translate"))
    btn.row(*nav_buttons)  
    btn.adjust(2)  
    await call.message.answer(text=_("choose_first_language"), reply_markup=btn.as_markup())
    await state.set_state(LanguageState.first_lang)


