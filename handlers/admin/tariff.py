from aiogram import types, F, html
from loader import bot, dp, db
from states.my_state import Tarif_add, Tarif_delete
from filters.my_filter import IsAdmin
from aiogram.fsm.context import FSMContext
from keyboards.default.button import get_before_url, send_button, admin_button, rek_types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.i18n import gettext as _
from aiogram.filters.callback_data import CallbackData


class Tarif(CallbackData, prefix="tariff"):
    check: bool

def tariff_check_button():
    btn = InlineKeyboardBuilder()
    btn.button(text="✅ Ha", callback_data=Tarif(check=True))
    btn.button(text="❌ Yo'q", callback_data=Tarif(check=False))
    btn.adjust(2)
    return btn.as_markup()

class Tarif_Delete(CallbackData, prefix="tariff_pre"):
    check: bool

def tariff_check_button_delete():
    btn = InlineKeyboardBuilder()
    btn.button(text="✅ Ha", callback_data=Tarif_Delete(check=True))
    btn.button(text="❌ Yo'q", callback_data=Tarif_Delete(check=False))
    btn.adjust(2)
    return btn.as_markup()

@dp.message(F.text == "🎁 Premium", IsAdmin())
async def premium_(message: types.Message, state: FSMContext):
    data = db.select__all_tarif()
    btn = InlineKeyboardBuilder()

    if not data:
        btn.button(text="Tarif qo'shish", callback_data="add_tariff"),
        btn.button(text=_("back_to_main_menu"), callback_data="main_menu_back"),
        await message.answer(
            text="Tariflar mavjud emas",
            reply_markup=btn.as_markup()
        )
        return
    text = ""
    for i in data:
        # btn.button(text=f"ID: {i[0]}  {i[2]} - {i[1]} ta", callback_data=f"tariff_{i[1]}_{i[2]}")
        text += f"ID: {i[0]}  {i[2]} - {i[1]} ta\n"
    btn.adjust(1)
    btn.button(text="Tarif qo'shish", callback_data="add_tariff")
    btn.button(text="Tarif o'chirish", callback_data="delete_tariff")
    btn.button(text=_("back_to_main_menu"), callback_data="main_menu_back")
    btn.adjust(2)  

    await message.answer(text=f"♻️ Tariflar\n\n{text}", reply_markup=btn.as_markup())



@dp.callback_query(F.data == "add_tariff", IsAdmin())
async def add_tariff(call: types.CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    await state.set_state(Tarif_add.start)
    btn = InlineKeyboardBuilder()
    btn.button(text=_("back_to_main_menu"), callback_data="main_menu_back")
    await call.message.answer(text="Tarif Narxini Kiriting: \n example(1$)", reply_markup=btn.as_markup())


@dp.message(Tarif_add.start, IsAdmin())
async def add_tariff(message: types.Message, state: FSMContext):
    await state.update_data({'price': message.text})
    btn = InlineKeyboardBuilder()
    btn.button(text=_("back_to_main_menu"), callback_data="main_menu_back")
    await message.answer(text="Tarif sonini kiriting raqamlarda: \n example(100)", reply_markup=btn.as_markup())
    await state.set_state(Tarif_add.check)


@dp.message(Tarif_add.check, IsAdmin())
async def check_tarif(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data({'amount': message.text})
        datas = await state.get_data()
        await message.answer(text=f"Tastiqlaysizmi?\nTarif Narxi {datas['price']}\nTarif soni {datas['amount']}", reply_markup=tariff_check_button())
        await state.set_state(Tarif_add.finish)
    else:
        await message.answer(text="Raqamlarda kiriting!!")
        await state.set_state(Tarif_add.check)


@dp.callback_query(Tarif.filter(), Tarif_add.finish, IsAdmin())
async def check(call: types.CallbackQuery, state: FSMContext, callback_data: Tarif):
    await call.answer(cache_time=60)
    data = callback_data.check
    if data:
        datas = await state.get_data()
        db.add_tarif(amount=datas['amount'],  price=datas['price'])
        await call.message.answer(text=f"✅ Tarif qo'shildi:", reply_markup=admin_button())
        return
    await call.message.answer(text="⚙️ Admin Panel", reply_markup=admin_button())



@dp.callback_query(F.data == "delete_tariff", IsAdmin())
async def delete_tariff(call: types.CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    btn = InlineKeyboardBuilder()
    btn.button(text=_("back_to_main_menu"), callback_data="main_menu_back")
    await call.message.answer(text="Tarif ID kiriting: \n example(1)", reply_markup=btn.as_markup())
    await state.set_state(Tarif_delete.start)


@dp.message(Tarif_delete.start, IsAdmin())
async def check_delete(msg: types.Message, state: FSMContext):
    data = db.select_tarif(tarfi_id=msg.text.strip())
    await state.update_data({'tarif_id': msg.text.strip()})
    if data:
        await msg.answer(text=f"Tastiqlaysizmi?\nTarif ID: {data[0]}\nTarif Narxi: {data[2]}\nTarif soni: {data[1]}", reply_markup=tariff_check_button_delete())
        await state.set_state(Tarif_delete.end)
    else:
        await msg.answer(text="Tarif mavjud emas id xato kiritildi:")
        return
    
@dp.callback_query(Tarif_Delete.filter(), Tarif_delete.end, IsAdmin())
async def delete_tariff(call: types.CallbackQuery, state: FSMContext, callback_data: Tarif):
    await call.answer(cache_time=60)
    data = callback_data.check
    get_id = await state.get_data()
    if data:
        db.delete_tarif(tarfi_id=get_id['tarif_id'])
        await call.message.answer(text="✅ Tarif muvafaqiyatli o'chirildi", reply_markup=admin_button())
        return
    await call.message.answer(text="⚙️ Admin Panel", reply_markup=admin_button())
