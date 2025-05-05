# import handlers,middlewares
# from loader import dp,bot,db
# from aiogram.types.bot_command_scope_all_private_chats import BotCommandScopeAllPrivateChats
# import asyncio
# from utils.notify_admins import start,shutdown
# from utils.set_botcommands import commands
# # Info
# import logging
# import sys
# from aiogram.types.menu_button_web_app import MenuButtonWebApp
# from aiogram.types.web_app_info import WebAppInfo
# from data.config import MINI_APP_URL
# from middlewares.my_middleware import UserCheckMiddleware
# from aiogram.utils.i18n import I18n
# from aiogram.types import Update
# from aiogram import BaseMiddleware


# async def setup_bot():
#     try:
#         await bot.set_my_commands(commands=commands, scope=BotCommandScopeAllPrivateChats(type='all_private_chats'))
        
#         await bot.set_chat_menu_button(
#             menu_button=MenuButtonWebApp(type='web_app', text='AI Assistant', web_app=WebAppInfo(url=MINI_APP_URL))
#         )
#         i18n = I18n(path="locales", default_locale="uz", domain="messages")
#         class I18nMiddleware(BaseMiddleware):
#             async def __call__(self, handler, event: Update, data: dict):
#                 user_id = None

#                 if event.message:
#                     user_id = event.message.from_user.id
#                 elif event.callback_query:
#                     user_id = event.callback_query.from_user.id
#                 else:
#                     return await handler(event, data)

#                 user_lang = db.get_user_lang(user_id)  
#                 if user_lang:
#                     i18n.ctx_locale.set(user_lang)

#                     data["_"] = i18n.gettext

#                 return await handler(event, data)
#         i18n_middleware = I18nMiddleware()
#         dp.update.middleware(i18n_middleware)
#         dp.message.middleware(UserCheckMiddleware())
        
#         try:
#             db.create_table_users()
#             db.create_table_channel_ids()
#             db.create_table_reklama_ids()
#             db.create_user_fetch_table()
#             db.create_table_user_chats()
#             db.create_table_user_chats_or_bots()
#         except Exception as e:
#             logging.error(f"Database error: {e}")
        
#         dp.startup.register(start)
#         dp.shutdown.register(shutdown)
        
#     except Exception as e:
#         logging.error(f"Setup error: {e}")
#     finally:
#         pass

import handlers, middlewares
from loader import dp, bot, db
from aiogram.types.bot_command_scope_all_private_chats import BotCommandScopeAllPrivateChats
import asyncio
from utils.notify_admins import start, shutdown
from utils.set_botcommands import commands
import logging
import sys
from aiogram.types.menu_button_web_app import MenuButtonWebApp
from aiogram.types.web_app_info import WebAppInfo
from data.config import MINI_APP_URL
from middlewares.my_middleware import UserCheckMiddleware
from aiogram.utils.i18n import I18n, SimpleI18nMiddleware
from aiogram.types import Update, CallbackQuery, Message
from aiogram import BaseMiddleware
from middlewares.my_middleware import CustomI18nMiddleware
# 🌍 I18n sozlash
i18n = I18n(path="locales", default_locale="uz", domain="messages")


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout), 
        logging.FileHandler('bot.log', mode='a', encoding='utf-8')  
    ]
)

async def setup_bot():
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await bot.set_my_commands(commands=commands, scope=BotCommandScopeAllPrivateChats(type='all_private_chats'))
        
        await bot.set_chat_menu_button(
            menu_button=MenuButtonWebApp(type='web_app', text='AI Assistant', web_app=WebAppInfo(url=MINI_APP_URL))
        )


        dp.update.middleware(CustomI18nMiddleware(i18n=i18n))
        dp.message.middleware(UserCheckMiddleware())  

        # 🛠 Database jadval yaratish
        try:
            db.create_table_users()
            db.create_table_channel_ids()
            db.create_table_reklama_ids()
            db.create_user_fetch_table()
            db.create_table_user_chats()
            db.create_table_user_chats_or_bots()
        except Exception as e:
            logging.error(f"Database error: {e}")

        dp.startup.register(start)
        dp.shutdown.register(shutdown)
        await dp.start_polling(bot)


    except Exception as e:
        logging.error(f"Setup error: {e}")
    finally:
        print('create')
        db.create_table_referal()
        db.create_user_fetch_table()
        db.create_table_referal_count()
        db.create_table_tarif()


if __name__=='__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(setup_bot())




