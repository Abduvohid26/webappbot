from aiogram import types, F, html
from loader import bot, dp, db
from states.my_state import ReklamaAddCount
from filters.my_filter import IsAdmin
from aiogram.fsm.context import FSMContext
from keyboards.default.button import get_before_url, send_button, admin_button, rek_types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData


class ReklamaCallback(CallbackData, prefix='ikb'):
    check:bool

def rekalam_callback_button():
    btn = InlineKeyboardBuilder()
    btn.button(text="✅ Ha", callback_data=ReklamaCallback(check=True))
    btn.button(text="❌ Yo'q", callback_data=ReklamaCallback(check=False))
    btn.adjust(2)
    return btn.as_markup()


@dp.message(F.text == "🔢 Reklama ko'rish soni", IsAdmin())
async def find_counter(msg: types.Message, state: FSMContext):
    btn = InlineKeyboardBuilder()
    btn.button(text="🔄 O'zgartirish", callback_data="update_reklama_count")
    btn.button(text="↩️ Orqaga", callback_data="back_reklama_count")
    btn.adjust(2)
    data = db.select_all_reklama()
    await msg.answer(text=f"Reklama ko'rish soni: {data[0][1]}", reply_markup=btn.as_markup())
    await state.set_state(ReklamaAddCount.start)

@dp.callback_query(lambda query: query.data == "update_reklama_count", ReklamaAddCount.start, IsAdmin())
async def new_count_get(call: types.CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    await call.message.answer(text="Reklama sonini kiriting raqamlarda")
    await state.set_state(ReklamaAddCount.finish)

@dp.message(ReklamaAddCount.finish, IsAdmin())
async def get_count(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data({'number': message.text})
        await message.answer(text="Tastiqlaysizmi?", reply_markup=rekalam_callback_button())
        await state.set_state(ReklamaAddCount.check)
        return
    else:
        await message.answer(text="Raqamlarda kiriting!!")
        await state.set_state(ReklamaAddCount.finish)

@dp.callback_query(ReklamaCallback.filter(), ReklamaAddCount.check, IsAdmin())
async def check(call: types.CallbackQuery, state: FSMContext, callback_data: ReklamaCallback):
    await call.answer(cache_time=60)
    data = callback_data.check
    if data:
        datas = await state.get_data()
        db.add_reklama(count=datas['number'])
        await call.message.answer(text=f"Reklama soni yangilandi: {datas['number']}", reply_markup=admin_button())
        return
    await call.message.answer(text="⚙️ Admin Panel", reply_markup=admin_button())

@dp.callback_query(F.data == "back_reklama_count", IsAdmin())
async def get_back(call: types.CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    await state.clear()
    await call.message.answer(text="⚙️ Admin Panel", reply_markup=admin_button())
