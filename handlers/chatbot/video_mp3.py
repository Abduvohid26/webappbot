from aiogram.fsm.context import FSMContext
from loader import dp, db
from aiogram import types, F
from data.config import OPENAI_KEY
from openai import OpenAI
from loader import bot
from aiogram.enums.chat_action import ChatAction
from states.my_state import VideoTranslate, Vidoe_Translate_State
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
import subprocess
import aiohttp
import io
from aiogram.types import BufferedInputFile
import aiofiles
from pathlib import Path
from aiogram.types import FSInputFile


BASE_DIR = Path(__file__).resolve().parent.parent.parent

client = OpenAI(
    api_key=OPENAI_KEY
)



languages = {
    "Uzbek 🇺🇿": "uzbek",
    "Turkish 🇹🇷": "turkish",
    "Kazakh 🇰🇿": "kazakh",
    "Azerbaijani 🇦🇿": "azerbaijani",
    "Turkmen 🇹🇲": "turkmen",
    "Tatar 🇷🇺": "tatar",
    "Kyrgyz 🇰🇬": "kyrgyz",
    
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
    "Lithuanian 🇱🇹": "lithuanian",
    "Latvian 🇱🇻": "latvian",
    "Estonian 🇪🇪": "estonian",
    "Belarusian 🇧🇾": "belarusian",
    
    # Osiyo tillari
    "Chinese 🇨🇳": "chinese",
    "Japanese 🇯🇵": "japanese",
    "Korean 🇰🇷": "korean",
    "Mongolian 🇲🇳": "mongolian",
    "Tajik 🇹🇯": "tajik",
    "Hindi 🇮🇳": "hindi",
    "Bengali 🇧🇩": "bengali",
    "Urdu 🇵🇰": "urdu",
    "Persian 🇷🇺": "persian",
    "Pashto 🇵🇰": "pashto",
    "Punjabi 🇵🇰": "punjabi",
    "Tamil 🇵🇰": "tamil",
    "Telugu 🇵🇰": "telugu",
    "Marathi 🇵🇰": "marathi",
    "Gujarati 🇵🇰": "gujarati",
    "Malayalam 🇵🇰": "malayalam",
    "Kannada 🇵🇰": "kannada",
    "Sinhala 🇱🇰": "sinhala",
    "Nepali 🇳🇵": "nepali",
    "Thai 🇹🇭": "thai",
    "Burmese 🇲🇲": "burmese",
    "Vietnamese 🇻🇳": "vietnamese",
    "Malay 🇲🇼": "malay",
    "Indonesian 🇮🇩": "indonesian",
    "Filipino 🇵🇪": "filipino",
    "Hebrew 🇮🇱": "hebrew",
    "Georgian 🇬🇪": "georgian",
    "Armenian 🇦🇲": "armenian",
    
    # Arab va Afrika tillari
    "Arabic 🇸🇪": "arabic",
    "Swahili 🇰🇾": "swahili",
    "↩️ Orqaga": "back_button_translate"
}

PER_PAGE = 10

from aiogram.enums.chat_action import ChatAction
from aiogram.utils.i18n import gettext as _
BASE_DIR = Path(__file__).resolve().parent.parent.parent

@dp.callback_query(F.data == "video_translate_")
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
    await state.set_state(Vidoe_Translate_State.start)



@dp.callback_query(F.data.startswith("page1_"))
async def pagination_handler(call: types.CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    page = int(call.data.split("_")[1])
    await call.message.edit_text(text=_("choose_translation_language"), reply_markup=await get_language_menu1(page))
    await state.set_state(Vidoe_Translate_State.start)

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

@dp.callback_query(Vidoe_Translate_State.start)
async def start_video(call: types.CallbackQuery, state: FSMContext):
    lang_name = call.data.split("_")[-1]
    await state.update_data({"lang": lang_name})
    btn = InlineKeyboardBuilder()
    btn.button(text=_("back_to_main_menu"), callback_data="language_back_button_translate")
    await call.message.answer(text=_("send_video"), reply_markup=btn.as_markup())
    await state.set_state(Vidoe_Translate_State.finish)




@dp.message(Vidoe_Translate_State.finish, MyFilter())
async def get_video(msg: types.Message, state: FSMContext):
    btn = InlineKeyboardBuilder()
    btn.button(text=_("back_to_main_menu"), callback_data="language_back_button_translate")
    if not msg.video:
        await msg.answer(_("please_send_video"), reply_markup=btn.as_markup())
        return
    await bot.send_chat_action(chat_id=msg.chat.id, action=ChatAction.UPLOAD_VIDEO)
    await msg.answer(_("video_translating"))

    # Tanlangan tilni olish
    data = await state.get_data()
    lang_name = data["lang"]
    
    # Video faylni yuklab olish
    video_file = await bot.get_file(msg.video.file_id)
    video_url = f"https://api.telegram.org/file/bot{bot.token}/{video_file.file_path}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(video_url) as resp:
                video_data = await resp.read()
    except Exception as e:
        print(e)
    finally:
        await session.close()

    # Videodan audio olish
    audio_data = await extract_audio(video_data)

    if not audio_data:
        await msg.answer(_("video_no_audio"))
        return

    audio, text, file_delete = await transcribe_audio(audio_data, lang_name)

    if "Xatolik yuz berdi" in text:
        await msg.answer(_("video_error"))
    else:
        btn = InlineKeyboardBuilder()
        btn.button(text=_("back_to_main_menu"), callback_data="language_back_button_translate")
        await msg.answer_audio(FSInputFile(audio), caption=f'📝 Matn:\n{text} \n\n{_("best_ai_bot")}', reply_markup=btn.as_markup())
        if os.path.exists(file_delete):
            os.remove(file_delete)

async def extract_audio(video_bytes: bytes) -> bytes:
    """ Videodan audioni ajratib WAV formatida saqlaydi """
    temp_video_path = "temp_video.mp4"
    temp_audio_path = "temp_audio.wav"

    async with aiofiles.open(temp_video_path, "wb") as f:
        await f.write(video_bytes)

    # 2️⃣ FFmpeg bilan audio ajratish
    command = [
        "ffmpeg", "-i", temp_video_path,  # Kiruvchi video
        "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1", "-f", "wav", temp_audio_path
    ]
    
    process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    if process.returncode != 0:
        print(f"❌ FFmpeg xatosi: {process.stderr.decode()}")
        return None

    async with aiofiles.open(temp_audio_path, "rb") as f:
        audio_bytes = await f.read()

    # 4️⃣ Foydalanilgan fayllarni o‘chirish
    os.remove(temp_video_path)
    os.remove(temp_audio_path)

    return audio_bytes

async def transcribe_audio(audio_bytes: bytes, lang_name: str) -> str:
    """ OpenAI Whisper-1 yordamida audioni matnga o‘girish """
    file_like = io.BytesIO(audio_bytes)
    file_like.name = "audio.wav"

    transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=file_like,
    ).text

    translation_prompt = f"Quyidagi matnni {lang_name} tiliga aniq tarjima qiling."
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
        voice="alloy",
        input=translated_text,
        response_format="mp3",
    )

    output_dir = BASE_DIR / "media/mp3_extract"
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = output_dir / f"output_{int(time.time())}.mp3"
    file_delete = output_path
    tts_response.stream_to_file(output_path)

    return str(output_path), translated_text, file_delete
