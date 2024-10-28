import logging
import random
from datetime import timedelta

from aiogram import F, Router, types
from aiogram.types import CallbackQuery, LabeledPrice
from aiogram_dialog import DialogManager

from database.premium import add_premium
from kb import payment_crypto_keyboard, payment_keyboard, premium_keyboard
from loader import crypto
from states import user_button
from text import PREMIUM_TEXT, responses

premium_router = Router()


async def send_payment_method_selection(callback, user_id, unique_id):
    markup = await premium_keyboard(unique_id)
    await callback.bot.send_message(user_id, f"{PREMIUM_TEXT} Выберите способ оплаты премиума:",
                                    reply_markup=markup)


@premium_router.callback_query(F.data.startswith("pay_stars_"))
async def pay_with_stars(callback: CallbackQuery, dialog_manager: DialogManager):
    unique_id = callback.data.split('_')[-1]
    if unique_id not in user_button or user_button[unique_id] != str(callback.from_user.id):
        await callback.answer(random.choice(responses), show_alert=True)
        return
    try:
        prices = [LabeledPrice(label="XTR", amount=35)]
        await callback.message.answer_invoice(
            title="🌟 Комару премиум",
            description="Покупка комару премиума",
            prices=prices,
            provider_token="",
            payload="komaru_premium",
            currency="XTR",
            reply_markup=await payment_keyboard(),
        )
        await callback.bot.delete_message(callback.message.chat.id, callback.message.message_id)
    except Exception as e:
        await callback.message.answer(f"Произошла ошибка: {str(e)}")
        logging.error(f"Error in pay_with_stars: {e}")


async def handle_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    await pre_checkout_query.bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


async def handle_successful_payment(message: types.Message):
    await add_premium(message.from_user.id, timedelta(days=30))
    await message.answer(
        '🌟 Спасибо за покупку Премиума! Наслаждайтесь эксклюзивными преимуществами.')


@premium_router.callback_query(F.data.startswith("pay_crypto_"))
async def create_and_send_invoice(callback: CallbackQuery, dialog_manager: DialogManager):
    try:
        invoice = await crypto.create_invoice(asset='USDT', amount=0.7)
        if not invoice:
            response = "Ошибка при создании инвойса. Попробуйте позже."
            await callback.bot.send_message(callback.from_user.id, response)
            return None

        markup = await payment_crypto_keyboard(invoice.invoice_id, invoice.bot_invoice_url)

        response = (
            f"Премиум активируется после подтверждения оплаты. Реквизиты: {invoice.bot_invoice_url}\n\nЦена: 0.70 USDT"
        )
        await callback.bot.delete_message(callback.message.chat.id, callback.message.message_id)
        await callback.bot.send_message(callback.from_user.id, response, reply_markup=markup)
        return invoice
    except Exception as e:
        error_message = f"Ошибка при создании инвойса: {e}"
        await callback.bot.send_message(callback.from_user.id, error_message)
        return None


@premium_router.callback_query(F.data.startswith("verify_payment"))
async def verify_payment(call, dialog_manager: DialogManager):
    parts = call.data.split('_')
    print(parts)
    if len(parts) < 3:
        await call.bot.send_message(call.message.chat.id, "Ошибка в данных платежа.")
        return

    action, context, invoice = parts[0], parts[1], parts[2]

    try:
        print("Invoice ID:", invoice)
        payment_status = await get_invoice_status(invoice)
        if payment_status == 'paid':
            await add_premium(call.from_user.id, timedelta(days=30))
            await call.bot.send_message(call.from_user.id,
                                        "🌟 Спасибо за покупку Премиума! Наслаждайтесь эксклюзивными преимуществами.")
            await call.bot.delete_message(call.message.chat.id, call.message.message_id)
        else:
            await call.bot.send_message(call.from_user.id, "Оплата не прошла! Попробуйте еще раз.")
    except Exception as e:
        await call.bot.send_message(call.from_user.id, f"Произошла ошибка при проверке статуса платежа: {str(e)}")


async def get_invoice_status(invoice_id):
    try:
        print(invoice_id)
        invoice = await crypto.get_invoices(invoice_ids=int(invoice_id))
        return invoice.status
    except Exception as e:
        print(f"Ошибка при получении данных инвойса: {e}")
        return None


premium_router.pre_checkout_query.register(handle_pre_checkout_query)
premium_router.message.register(handle_successful_payment, F.successful_payment)
