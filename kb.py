from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types
from aiogram.types import Message
import random
from states import user_button


async def start_kb(msg: Message):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(
        text="➡️ Добавить в группу",
        url="https://t.me/KomaruCardsBot?startgroup=komaru&admin=change_info+restrict_members+"
            "delete_messages+pin_messages+invite_users"))
    return builder.as_markup()


async def help_kb(msg: Message):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🔉 Наш канал", url="t.me/komaru_updates"))
    builder.row(types.InlineKeyboardButton(text="📝 Пользовательское соглашение",
                                           url="https://telegra.ph/Polzovatelskoe-soglashenie-06-17-6"))
    return builder.as_markup()


async def profile_kb(msg: Message):
    unique_id = str(random.randint(10000, 9999999999))
    user_button[unique_id] = str(msg.from_user.id)
    builder = InlineKeyboardBuilder()
    button_1 = types.InlineKeyboardButton(text="🃏 Мои карточки", callback_data=f'show_cards_{unique_id}')
    button_2 = types.InlineKeyboardButton(text="🀄️ Топ карточек", callback_data=f'top_komaru_{unique_id}')
    button_3 = types.InlineKeyboardButton(text="💎 Премиум", callback_data=f'premium_callback_{unique_id}')
    builder.add(button_1, button_2, button_3)
    return builder.as_markup()


async def cards_kb(rarities):
    builder = InlineKeyboardBuilder()
    for rarity in rarities:
        callback_data = f'show_{rarity[:15]}'
        builder.add(types.InlineKeyboardButton(text=rarity, callback_data=callback_data))
    return builder.as_markup()


async def get_card_navigation_keyboard(user_id, card_index, rarity, rarity_cards, card_id):
    builder = InlineKeyboardBuilder()
    love_button = types.InlineKeyboardButton(text="❤️", callback_data=f'love_{user_id}_{card_id}')
    builder.add(love_button)

    if card_index > 0:
        prev_button = types.InlineKeyboardButton(text="⬅️",
                                                 callback_data=f'navigate_{user_id}_prev_'
                                                               f'{card_index - 1}_{rarity[:15]}')
        builder.add(prev_button)

    if card_index < len(rarity_cards) - 1:
        next_button = types.InlineKeyboardButton(text="➡️",
                                                 callback_data=f'navigate_{user_id}_next_'
                                                               f'{card_index + 1}_{rarity[:15]}')
        builder.add(next_button)

    return builder.as_markup()


async def top_kb(callback, choice):
    builder = InlineKeyboardBuilder()
    if choice == "all_top":
        unique_id = str(random.randint(10000, 9999999999))
        user_button[unique_id] = str(callback.from_user.id)
        button_1 = types.InlineKeyboardButton(text="🃏 Топ по карточкам",
                                              callback_data=f'top_cards_cards_{unique_id}')
        button_2 = types.InlineKeyboardButton(text="💯 Топ по очкам",
                                              callback_data=f'top_cards_point_{unique_id}')
        button_3 = types.InlineKeyboardButton(text="⌛️ Топ за все время",
                                              callback_data=f'top_cards_all_{unique_id}')
        builder.add(button_1, button_2, button_3)
        return builder.as_markup()
    elif choice == "cards":
        unique_id = str(random.randint(10000, 9999999999))
        user_button[unique_id] = str(callback.from_user.id)
        button_1 = types.InlineKeyboardButton(text="💯 Топ по очкам",
                                              callback_data=f'top_cards_point_{unique_id}')
        button_2 = types.InlineKeyboardButton(text="⌛️ Топ за все время",
                                              callback_data=f'top_cards_all_{unique_id}')
        builder.add(button_1, button_2)
        return builder.as_markup()
    elif choice == "point":

        unique_id = str(random.randint(10000, 9999999999))
        user_button[unique_id] = str(callback.from_user.id)
        button_1 = types.InlineKeyboardButton(text="🃏 Топ по карточкам",
                                              callback_data=f'top_cards_cards_{unique_id}')
        button_2 = types.InlineKeyboardButton(text="⌛️ Топ за все время",
                                              callback_data=f'top_cards_all_{unique_id}')
        builder.add(button_1, button_2)
        return builder.as_markup()
    elif choice == "all":

        unique_id = str(random.randint(10000, 9999999999))
        user_button[unique_id] = str(callback.from_user.id)
        button_1 = types.InlineKeyboardButton(text="🃏 Топ по карточкам",
                                              callback_data=f'top_cards_cards_{unique_id}')
        button_2 = types.InlineKeyboardButton(text="💯 Топ по очкам",
                                              callback_data=f'top_cards_point_{unique_id}')
        builder.add(button_1, button_2)
        return builder.as_markup()


async def premium_keyboard(unique_id):
    builder = InlineKeyboardBuilder()
    stars_button = types.InlineKeyboardButton(text="Telegram Stars", callback_data=f"pay_stars_{unique_id}")
    crypto_button = types.InlineKeyboardButton(text="CryptoBot", callback_data=f"pay_crypto_{unique_id}")
    builder.add(stars_button, crypto_button)
    return builder.as_markup()


async def payment_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text=f"Оплатить 35 ⭐️", pay=True)

    return builder.as_markup()


async def payment_crypto_keyboard(invoice_id, invoice_url):
    builder = InlineKeyboardBuilder()
    pay_button = types.InlineKeyboardButton(text="Оплатить", url=invoice_url)
    paid_button = types.InlineKeyboardButton(text="Я оплатил",
                                             callback_data=f"verify_payment_{invoice_id}")
    builder.add(pay_button, paid_button)
    return builder.as_markup()


async def subscribe_keyboard():
    builder = InlineKeyboardBuilder()
    subscribe_button = types.InlineKeyboardButton(text="Подписаться", url="https://t.me/komaru_updates")
    builder.add(subscribe_button)
    return builder.as_markup()
