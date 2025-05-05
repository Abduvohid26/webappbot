from aiogram import BaseMiddleware
from aiogram.types import Message,Update
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import *
from loader import bot, db
from utils.misc.subscription import checksubscription
from aiogram.filters.callback_data import CallbackData

class CheckSubCallback(CallbackData,prefix='check'):
    check :bool
class UserCheckMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> bool:
        btn = InlineKeyboardBuilder()
        user = event.from_user
        final_status = True
        CHANNELS = db.select_all_channels()
        if CHANNELS:
            for channel in CHANNELS:
                status = True
                try:
                    status = await checksubscription(user_id=user.id, channel=channel[-1])
                except Exception as e:
                    print(f"Subscription check error: {e}")

                final_status = final_status and status

                try:
                    chat = await bot.get_chat(chat_id=channel[-1])
                    if status:
                        btn.button(text=f"✅ {chat.title}", url=f"{await chat.export_invite_link()}")
                    else:
                        btn.button(text=f"❌ {chat.title}", url=f"{await chat.export_invite_link()}")
                except Exception as e:
                    print(e)
                    pass

            if final_status:
                await handler(event, data)
            else:
                btn.button(
                    text="🔄 Tekshirish",
                    callback_data=CheckSubCallback(check=False)
                )
                btn.adjust(1)
                await event.answer(
                    "Iltimos bot to'liq ishlashi uchun quyidagi kanal(lar)ga obuna bo'ling!",
                    reply_markup=btn.as_markup()
                )
        else:
            await handler(event, data)


from aiogram import BaseMiddleware
from aiogram.types import Update
from typing import Callable, Dict, Awaitable, Any
from loader import db, i18n  # ✅ i18n ni loader.py dan import qilamiz
from aiogram.utils.i18n import I18nMiddleware
from aiogram.types import TelegramObject



class CustomI18nMiddleware(I18nMiddleware):
    async def get_locale(self, event: TelegramObject, data: Dict[str, Any]) -> str:
        user_id = None

        if hasattr(event, "message") and event.message:
            user_id = event.message.from_user.id
        elif hasattr(event, "callback_query") and event.callback_query:
            user_id = event.callback_query.from_user.id

        if user_id:
            return db.get_user_lang(user_id) or self.default_locale  # 🌍 Tilni bazadan olish
        
        return self.default_locale  # 🌍 Default til
        

    # async def __call__(
    #     self, handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]], event: Update, data: Dict[str, Any]
    # ) -> Any:
    #     user_id = None

    #     if event.message:
    #         user_id = event.message.from_user.id
    #     elif event.callback_query:
    #         user_id = event.callback_query.from_user.id
    #     else:
    #         return await handler(event, data)

    #     # 🏆 Foydalanuvchi tilini bazadan olish
    #     user_lang = db.get_user_lang(user_id) or "uz"
    #     print(user_lang, 'lang')
    #     if user_lang:
    #         i18n.ctx_locale.set(user_lang)  # ✅ I18n kontekstni o‘rnatish
    #         data["_"] = i18n.gettext  # ✅ Tarjima funksiyasini berish

    #     return await handler(event, data)
