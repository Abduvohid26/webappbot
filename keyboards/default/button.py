from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton, InlineKeyboardMarkup, \
    ReplyKeyboardBuilder
from aiogram.filters.callback_data import CallbackData


# def menu_button():
#     btn = InlineKeyboardBuilder()
#     btn.button(text="🧮 Image Generate", callback_data='image_generate_bot')
#     btn.button(text="🗣 Voice to Text", callback_data='voice_generate_text')
#     btn.button(text="📝 Text to Voice", callback_data='text_generate_voice')
#     btn.button(text="🏞 Image Analyze", callback_data='analyze_image')
#     btn.button(text="📱 Text summarization", callback_data='text_summarization_bot')
#     btn.adjust(2)
#     return btn.as_markup()
#

from aiogram.types.web_app_info import WebAppInfo
from aiogram.utils.i18n import gettext as _
from data.config import MINI_APP_URL, MINI_APP_URLJ
# def menu_button():
#     button = InlineKeyboardMarkup(
#         inline_keyboard=[
#             # [InlineKeyboardButton(text="🧮 Image Generate", callback_data='image_generate_bot')
#             [InlineKeyboardButton(text="🗣 Voice to Text", callback_data='voice_generate_text'),InlineKeyboardButton(text="📝 Text to Voice", callback_data='text_generate_voice')],
#             [InlineKeyboardButton(text="🏞 Image Analyze", callback_data='analyze_image'),InlineKeyboardButton(text="📁 Document Q&A ", callback_data="document_q_a")],
#             [InlineKeyboardButton(text="📱 Text summarization", callback_data='text_summarization_bot')],   
#             [InlineKeyboardButton(text="♻️ Translate", callback_data="translater_bot"), InlineKeyboardButton(text="🗣 Voice Translate", callback_data="voice_translate")],
#             [InlineKeyboardButton(text="📹 Video translate", callback_data="video_translate_")],
#             [InlineKeyboardButton(text="🌍 Change Language", callback_data="change_language_main")],
#             [InlineKeyboardButton(text="🤖  AI Assistant", web_app=WebAppInfo(url=MINI_APP_URLJ))]
#         ]
#     )
#     return button
def menu_button():
    button = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=_("🗣 Voice to Text"), callback_data='voice_generate_text'), 
                InlineKeyboardButton(text=_("📝 Text to Voice"), callback_data='text_generate_voice')
            ],
            [
                InlineKeyboardButton(text=_("🏞 Image Analyze"), callback_data='analyze_image'), 
                InlineKeyboardButton(text=_("📁 Document Q&A "), callback_data="document_q_a")
            ],
            [
                InlineKeyboardButton(text=_("📱 Text summarization"), callback_data='text_summarization_bot')
            ],
            [
                InlineKeyboardButton(text=_("♻️ Translate"), callback_data="translater_bot"), 
                InlineKeyboardButton(text=_("🗣 Voice Translate"), callback_data="voice_translate")
            ],
            [
                InlineKeyboardButton(text=_("📹 Video Translate"), callback_data="video_translate_"),
                InlineKeyboardButton(text=_("🏞 Image Text Translate"), callback_data="image_translate_")
            ],
            [
                InlineKeyboardButton(text=_("🌍 Change Language"), callback_data="change_language_main")
            ],
            [
                InlineKeyboardButton(text="🎁 Premium tarif", callback_data="referal_premium"),
                InlineKeyboardButton(text="👥 Referal", callback_data="referals")
            ],
            [
                InlineKeyboardButton(text=_("🤖 AI Assistant"), web_app=WebAppInfo(url=MINI_APP_URL))
            ]
        ]
    )
    return button


# def admin_button():
#     btn = InlineKeyboardBuilder()
#     btn.button(text='📲 Reklama Yuborish', callback_data='reklama_yuborish')
#     btn.button(text='👤 Obunachilar soni', callback_data='obunachilar_soni')
#     btn.button(text="🔢 Reklama ko'rish soni", callback_data='reklama_korish_soni')
#     btn.button(text='➕  Kanal qoshish', callback_data='kanal_qoshish')
#     btn.button(text='♾️ Kannnallar', callback_data='kanallar')
#     btn.button(text='✖️ Kanal o\'chirish', callback_data='kanal_ochirish')
#     btn.adjust(2)
#     return btn.as_markup()

def admin_button():
    btn = ReplyKeyboardBuilder()
    btn.button(text='📲 Reklama Yuborish')
    btn.button(text='👤 Obunachilar soni')
    btn.button(text="🔢 Reklama ko'rish soni")
    btn.button(text='➕  Kanal qo\'shish')
    btn.button(text='♾️ Kanallar')
    btn.button(text='✖️ Kanal o\'chirish')
    btn.button(text='🎁 Premium')
    btn.adjust(2)
    return btn.as_markup(resize_keyboard=True, one_time_keyboard=True)



def rek_types():
    btn = ReplyKeyboardBuilder()
    btn.button(text='📝 Text')
    btn.button(text='📷 Rasm')
    btn.button(text='📹 Video')
    btn.button(text='🔙 Orqaga')
    btn.adjust(2)
    return btn.as_markup(resize_keyboard=True)


def get_before_url():
    btn = ReplyKeyboardBuilder()
    btn.button(text='📌 Bekor qilish')
    btn.adjust(1)
    return btn.as_markup(resize_keyboard=True, one_time_keyboard=True)

def send_button():
    btn = ReplyKeyboardBuilder()
    btn.button(text='📤 Yuborish')
    btn.button(text='📌 Bekor qilish')
    btn.adjust(2)
    return btn.as_markup(resize_keyboard=True)


class DeleteChannelCallback(CallbackData, prefix='ikb'):
    check:bool

def delete_channel_verify():
    btn = InlineKeyboardBuilder()
    btn.button(text="✅ Ha", callback_data=DeleteChannelCallback(check=True))
    btn.button(text="❌ Yo'q", callback_data=DeleteChannelCallback(check=False))
    btn.adjust(2)
    return btn.as_markup()

def voices_button():
    btn = InlineKeyboardBuilder()
    voice_genders = {
        "Alloy": "🧑", "Ash": "🧑", "Coral": "👩", "Echo": "🧑", "Fable": "👩", 
        "Onyx": "🧑", "Nova": "👩", "Sage": "🧑", "Shimmer": "👩"
    }
    voices = ["Alloy", "Ash", "Coral", "Echo", "Fable", "Onyx", "Nova", "Sage", "Shimmer"]
    
    for voice in voices:
        emoji = voice_genders.get(voice, "")
        btn.button(text=f"{emoji} {voice}", callback_data=f"voicer_{voice.lower().strip()}")
    btn.button(text=_("back_to_main_menu"), callback_data=_("main_menu_back"))
    btn.adjust(2)
    return btn.as_markup()

def referal_button():
    btn = InlineKeyboardBuilder()
    btn.button(text="👥 Referal", callback_data="referals")
    btn.button(text=_("Premuium tarif"), callback_data="referal_premium")
    btn.button(text=_("back_to_main_menu"), callback_data="main_menu_back_referal")
    btn.adjust(1)
    return btn.as_markup()