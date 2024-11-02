import logging
import random

from aiogram import F, Router, types
from aiogram.types import InputMediaPhoto, Message
from aiogram.utils.text_decorations import html_decoration
from aiogram_dialog import DialogManager
from sqlalchemy import func

from database.cards import get_all_cards, get_card
from database.models import Card, User
from database.premium import check_premium
from database.top import get_me_on_top, get_top_users_by_all_points, get_top_users_by_cards, get_top_users_by_points
from database.user import get_user, set_love_card
from filters import NotCommentFilter, ProfileFilter
from handlers.premium import send_payment_method_selection
from kb import cards_kb, get_card_navigation_keyboard, profile_kb, top_kb
from loader import bot
from states import get_dev_titul, get_titul, user_button
from text import responses

profile_router = Router()


async def send_initial_card_with_navigation(chat_id, user_id, rarity, rarity_cards, card_index):
    if card_index < len(rarity_cards):
        card: Card = rarity_cards[card_index]
        photo_data = card.photo
        caption = f"{card.name}\nРедкость: {card.rarity}\n\nОчки: {str(card.points)}\n"

        markup = await get_card_navigation_keyboard(user_id, card_index, rarity, rarity_cards, card.id)

        await bot.send_photo(chat_id, photo=photo_data, caption=caption, reply_markup=markup)
    else:
        logging.error(f"Card index {card_index} out of range for rarity cards")


async def send_card_with_navigation(chat_id, message_id, user_id, rarity, rarity_cards, card_index):
    if card_index < len(rarity_cards):
        card: Card = rarity_cards[card_index]
        photo_data = card.photo
        caption = f"{card.name}\nРедкость: {card.rarity}\n\nОчки: {str(card.points)}\n"

        markup = await get_card_navigation_keyboard(user_id, card_index, rarity, rarity_cards, card.id)

        media = InputMediaPhoto(media=photo_data)
        await bot.edit_message_media(media=media, chat_id=chat_id, message_id=message_id)
        await bot.edit_message_caption(caption=caption, chat_id=chat_id, message_id=message_id, reply_markup=markup)
    else:
        logging.error(f"Card index {card_index} out of range for rarity cards")


@profile_router.message(ProfileFilter() or F.command("profile"), NotCommentFilter())
async def user_profile(msg: Message, dialog_manager: DialogManager):
    user_id = msg.from_user.id
    first_name = msg.from_user.first_name
    last_name = msg.from_user.last_name or ""
    user = await get_user(user_id)
    titul = await get_titul(user.card_count)
    collected_cards = len(user.cards)
    total_cards = len(await get_all_cards())
    favorite_card = await get_card(user.love_card)
    if favorite_card is None:
        favorite_card = "нету"
    else:
        favorite_card = favorite_card.name
    premium_status = await check_premium(user.premium_expire)
    premium_message = f"Премиум: активен до {user.premium_expire.date()}" if premium_status else "Премиум: не активен"

    if user_id in [6184515646, 1268026433, 5493956779, 1022923020, 851455143, 6794926384, 6679727618]:
        dev_titul = await get_dev_titul(user_id)
        dev_titul_message = f"<blockquote> 🪬 Dev Титул: {dev_titul} </blockquote>"
    else:
        dev_titul_message = ""

    try:
        user_profile_photos = await bot.get_user_profile_photos(user_id, limit=1)
        if user_profile_photos.photos:
            photo = user_profile_photos.photos[0][-1]
            file_id = photo.file_id

            photo_cache = file_id
        else:
            photo_cache = 'https://tinypic.host/images/2024/07/08/avatar.jpg'

        caption = (
            f"Привет {html_decoration.bold(html_decoration.quote(user.nickname))}!\n\n"
            f"🏡 Твой профиль:\n"
            f"🃏 Собрано {collected_cards} из {total_cards} карточек\n"
            f"💰 Очки: {user.points}\n"
            f"🎖️ Титул: {titul}\n"
            f"💖 Любимая карточка: {favorite_card}\n"
            f"🌟 {premium_message}\n"
            f"{dev_titul_message}\n"
            f"💡 Хочешь сменить ник? Введи <code>сменить ник &lt;ник&gt;</code>"
        )
        markup = await profile_kb(msg)

        await bot.send_photo(msg.chat.id, photo=photo_cache, caption=caption, reply_markup=markup, parse_mode="HTML")
    except Exception as e:
        if "bot was blocked by the user" in str(e):
            await msg.answer("Пожалуйста, разблокируйте бота для доступа к вашему профилю.")
        else:
            print(e)
            await msg.answer(
                "Произошла ошибка при доступе к вашему профилю. Попробуйте позже.")


@profile_router.message(ProfileFilter() or F.command("profile"))
async def user_profile_comments(msg: Message, dialog_manager: DialogManager):
    await msg.reply("Пожалуйста перейдите в чат для использования бота!")


@profile_router.callback_query(F.data.startswith("show_cards"))
async def show_cards_second(callback: types.CallbackQuery, dialog_manager: DialogManager):
    unique_id = str(callback.data.split('_')[-1])
    if unique_id not in user_button or user_button[unique_id] != str(callback.from_user.id):
        await callback.answer(text=random.choice(responses), show_alert=True)
        return

    user_id = callback.from_user.id
    cats = await get_all_cards()
    user_nickname = callback.from_user.first_name
    user = await get_user(user_id)
    collected_cards = len(user.cards)
    total_cards = len(cats)

    if user.cards:
        cats_owned_by_user = {(await get_card(cat)).name for cat in user.cards}
        rarities = {(await get_card(cat)).rarity for cat in user.cards}
        markup = await cards_kb(rarities)
        try:
            await bot.send_message(user_id,
                                   f"У вас собрано {collected_cards} из {total_cards} возможных\nВыберите редкость:",
                                   reply_markup=markup)
            if callback.message.chat.type in ["supergroup", "group"]:
                await bot.send_message(chat_id=callback.message.chat.id,
                                       text=f"{user_nickname}, карточки отправлены вам в личные сообщения!")
            else:
                pass
        except Exception as e:
            logging.error(f"Не удалось отправить сообщение: {str(e)}")
            await callback.answer("Напишите боту что-то в личные сообщения, чтобы отправить вам карточки!",
                                  show_alert=True)
    else:
        await callback.answer("Вы пока что не наблюдали за птичками.", show_alert=True)


@profile_router.callback_query(F.data.startswith("show_"))
async def show_cards(callback: types.CallbackQuery, dialog_manager: DialogManager):
    try:
        cats = await get_all_cards()
        rarity = callback.data[len('show_'):]
        user_id = callback.from_user.id
        user_nickname = callback.from_user.first_name
        user = await get_user(user_id)
        rarity_cards = []
        for cat in cats:
            if cat[0].id in user.cards and cat[0].rarity.startswith(rarity):
                rarity_cards.append(cat[0])

        if rarity_cards:
            first_card_index = 0
            await send_initial_card_with_navigation(callback.message.chat.id, user_id, rarity, rarity_cards,
                                                    first_card_index)
        else:
            await callback.message.answer(f"У вас нет карточек редкости {rarity}")
    except Exception as e:
        logging.error(f"Error in show_cards: {e}")
        await callback.message.answer("Произошла ошибка при отображении карточек.")


@profile_router.callback_query(F.data.startswith("love_"))
async def handle_love_card(callback: types.CallbackQuery):
    parts = callback.data.split('_')
    user_id, card_id = int(parts[1]), int(parts[2])

    card = await get_card(card_id)
    if card is not None:
        await set_love_card(user_id, card_id)
        await bot.answer_callback_query(callback.id, f"Карточка '{card.name}' теперь ваша любимая!")
    else:
        await bot.answer_callback_query(callback.id, "Не найдено карточек с таким ID.")


@profile_router.callback_query(F.data.startswith("navigate_"))
async def navigate_cards(callback: types.CallbackQuery):
    try:
        cats = await get_all_cards()
        parts = callback.data.split('_')
        user_id = int(parts[1])
        direction = parts[2]
        new_index = int(parts[3])
        rarity = parts[4]

        user = await get_user(user_id)
        rarity_cards = []
        for cat in cats:
            if cat[0].id in user.cards and cat[0].rarity.startswith(rarity):
                rarity_cards.append(cat[0])

        if 0 <= new_index < len(rarity_cards):
            await send_card_with_navigation(callback.message.chat.id, callback.message.message_id, user_id, rarity,
                                            rarity_cards, new_index)
        else:
            await callback.message.answer("Индекс карточки вне диапазона.")
    except Exception as e:
        logging.error(f"Error in navigate_cards: {str(e)}")
        await callback.message.answer("Произошла ошибка при навигации по карточкам.")


@profile_router.callback_query(F.data.startswith("top_komaru"))
async def top_komaru(callback: types.CallbackQuery):
    unique_id = str(callback.data.split('_')[-1])
    if unique_id not in user_button or user_button[unique_id] != str(callback.from_user.id):
        await callback.answer(random.choice(responses), show_alert=True)
        return
    markup = await top_kb(callback, "all_top")
    await callback.message.answer(
        text="Топ 10 пользователей по карточкам. Выберите кнопку:",
        reply_markup=markup)


@profile_router.callback_query(F.data.startswith("top_cards_"))
async def cards_top_callback(callback: types.CallbackQuery):
    parts = callback.data.split('_')
    choice = parts[2]
    unique_id = str(parts[-1])

    if unique_id not in user_button or user_button[unique_id] != str(callback.from_user.id):
        await callback.answer(random.choice(responses), show_alert=True)
        return

    user_id = callback.from_user.id
    user = await get_user(user_id)
    message_text = ""

    if choice == "cards":
        top = await get_top_users_by_cards()
        user_rank = await get_me_on_top(func.cardinality(User.cards), user_id)

        message_text = "🏆 Топ-10 пользователей по количеству собранных карточек:\n\n"
        for top_user in top:
            message_text += f"{top_user[0]}. {top_user[1]} {top_user[2]}: {top_user[3]} карточек"
            if user_id == 6184515646:
                message_text += f" (user_id: {top_user[4]})"
            message_text += "\n"

        if user_rank and user_rank > 10:
            message_text += (f"\nВаше место: {user_rank}"
                             f" ({user.nickname}: {len(user.cards)} карточек)")

        markup = await top_kb(callback, "cards")

    elif choice == "point":
        top = await get_top_users_by_points()
        user_rank = await get_me_on_top(User.points, user_id)

        message_text = "🏆 Топ-10 пользователей по количеству набранных очков:\n\n"
        for top_user in top:
            message_text += f"{top_user[0]}. {top_user[1]} {top_user[2]}: {top_user[3]} очков\n"
        if user_rank and user_rank > 10:
            message_text += (f"\nВаше место: {user_rank} "
                             f"({user.nickname}: {user.points} очков)")

        markup = await top_kb(callback, "point")

    elif choice == "all":
        top = await get_top_users_by_all_points()
        user_rank = await get_me_on_top(User.all_points, user_id)

        message_text = "🏆 Топ-10 пользователей по всем временам (очки):\n\n"
        for top_user in top:
            message_text += f"{top_user[0]}. {top_user[1]} {top_user[2]}: {top_user[3]} очков\n"

        if user_rank and user_rank > 10:
            message_text += (f"\nВаше место: {user_rank} "
                             f"({user.nickname}: {user.all_points} очков)")

        markup = await top_kb(callback, "all")
    else:
        markup = await top_kb(callback, "all")

    if not message_text:
        message_text = "Не удалось получить данные. Попробуйте позже."

    await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                text=message_text, reply_markup=markup)


@profile_router.callback_query(F.data.startswith("premium_callback"))
async def handler_premium(callback: types.CallbackQuery):
    unique_id = callback.data.split('_')[-1]
    if unique_id not in user_button or user_button[unique_id] != str(callback.from_user.id):
        await callback.answer(random.choice(responses), show_alert=True)
        return

    try:
        await send_payment_method_selection(callback, callback.from_user.id, unique_id)
        if callback.message.chat.type != "private":
            await callback.message.answer(
                f"{str(callback.from_user.first_name)}, "
                f"информация о способах оплаты отправлена вам в личные сообщения.")
    except Exception as e:
        print(e)
        await callback.answer("Пожалуйста, напишите боту что-то в личные сообщения, чтобы я смог отправить информацию.",
                              show_alert=True)
