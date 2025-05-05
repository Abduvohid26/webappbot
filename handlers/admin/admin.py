from filters.my_filter import IsAdmin
from aiogram.filters import Command
from aiogram import types, F
from loader import bot, db, dp
from keyboards.default.button import admin_button, rek_types
from aiogram.fsm.context import FSMContext



from check_url import get_db
@dp.message(Command("admin_get_db"), IsAdmin())
async def get_db_file(msg: types.Message):
    await get_db()
    await msg.answer(text="Db File")

@dp.message(Command('admin'), IsAdmin())
async def get_panel(message: types.Message):
    await message.answer(text="⚙️ Admin Panel", reply_markup=admin_button())


@dp.message(F.text == '👤 Obunachilar soni', IsAdmin())
async def users_count(message: types.Message):
    data = db.select_all_users()
    await message.answer(f"Botdagi faol foydalanuvchilar soni {len(data)} ta.")


@dp.message(F.text == '📲 Reklama Yuborish', IsAdmin())
async def rek_bot(message: types.Message):
    await message.answer('📲  Reklama yuborish turini tanlang:', reply_markup=rek_types())

@dp.message(F.text == '🔙 Orqaga', IsAdmin())
async def get_finish(msg: types.Message, state: FSMContext):
    await msg.answer(text="⚙️ Admin Panel", reply_markup=admin_button())
    await state.clear()



@dp.message(F.text == '📌 Bekor qilish', IsAdmin())
async def render_rek_type_panel(message: types.Message, state: FSMContext):
    await message.answer('📲  Reklama yuborish turini tanlang:', reply_markup=rek_types())
    await state.clear()
