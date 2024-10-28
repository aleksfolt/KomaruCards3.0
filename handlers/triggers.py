import os
import random
import sys

from aiogram.enums import ChatMemberStatus, ContentType
from aiogram.filters import ChatMemberUpdatedFilter
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.group import in_group_change
from database.promo import get_promo, promo_use

sys.path.insert(0, sys.path[0] + "..")
import re
from datetime import datetime, timedelta
import emoji
import sqlalchemy
from aiogram import F, Router, types
from aiogram.types import ChatMemberUpdated, InlineKeyboardButton, Message
from aiogram_dialog import DialogManager

sys.path.append(os.path.realpath('.'))
from aiogram.filters import IS_MEMBER, IS_NOT_MEMBER
from database.cards import get_all_cards
from database.models import Card
from database.user import add_card, add_points, change_username, check_last_get, get_user, \
    in_pm_change, update_last_get, is_nickname_taken, IsAlreadyResetException
from database.premium import check_premium
from filters.FloodWait import RateLimitFilter
from filters import CardFilter, NotCommentFilter
from loader import bot
from text import forbidden_symbols
import validators

text_triggers_router = Router()


@text_triggers_router.message(CardFilter(), NotCommentFilter(), RateLimitFilter(1.0))
async def komaru_cards_function(msg: Message, dialog_manager: DialogManager):
    user_id = msg.from_user.id
    user_nickname = msg.from_user.first_name
    username = msg.from_user.username
    user = await get_user(user_id)
    now = datetime.now()
    is_premium = await check_premium(user.premium_expire)

    if not await check_last_get(user.last_usage, is_premium):
        time_difference = now - user.last_usage
        hours = 3 if is_premium else 4
        difference = (datetime.min + (timedelta(hours=hours) - time_difference)).time()
        time_parts = []
        if difference.hour > 0:
            time_parts.append(f"{difference.hour} часов")
        if difference.minute > 0:
            time_parts.append(f"{difference.minute} минут")
        if difference.second > 0:
            time_parts.append(f"{difference.second} секунд")
        time_string = " ".join(time_parts)
        await msg.reply(
            f"{msg.from_user.first_name}, вы осмотрелись, но не увидели рядом Комару. "
            f"Попробуйте еще раз через {time_string}.")
        return
    chosen_cat: Card = await random_cat(is_premium)
    photo_data = chosen_cat.photo
    if chosen_cat.id in user.cards:
        await bot.send_photo(
            msg.chat.id,
            photo=photo_data,
            caption=f"✨{msg.from_user.first_name}, вы осмотрелись вокруг и снова увидели {chosen_cat.name}! "
                    f"✨\nБудут начислены только очки.\n\n🎲 "
                    f"Редкость: {chosen_cat.rarity}\n💯 +{chosen_cat.points} очков.\n🌟 "
                    f"Всего поинтов: {user.points + int(chosen_cat.points)}",
            reply_to_message_id=msg.message_id
        )
    else:
        await bot.send_photo(
            msg.chat.id,
            photo=photo_data,
            caption=f"✨{msg.from_user.first_name}, вы осмотрелись вокруг и увидели.. "
                    f"{chosen_cat.name}! ✨\n\n🎲 Редкость: {chosen_cat.rarity}\n💯 "
                    f"Очки: {chosen_cat.points}\n🌟 Всего поинтов: {user.points + int(chosen_cat.points)}",
            reply_to_message_id=msg.message_id
        )
        await add_card(user.telegram_id, chosen_cat.id)

    await update_last_get(user.telegram_id)
    await add_points(user.telegram_id, int(chosen_cat.points))


@text_triggers_router.message(F.text.casefold().startswith("сменить ник".casefold()))
async def change_nickname(message: types.Message, dialog_manager: DialogManager):
    user_id = message.from_user.id
    user = await get_user(user_id)
    first_name = message.from_user.first_name
    premium_status = await check_premium(user.premium_expire)

    parts = message.text.casefold().split('сменить ник'.casefold(), 1)
    if len(parts) > 1 and parts[1].strip():
        new_nick = parts[1].strip()

        if 5 > len(new_nick) or len(new_nick) > 32:
            await message.reply("Никнейм не должен быть короче 5 символов и длиннее 32 символов.")
            return

        if any(emoji.is_emoji(char) for char in new_nick):
            if not premium_status:
                await message.reply("Вы не можете использовать эмодзи в нике. Приобретите премиум в профиле!")
                return
        else:
            if not re.match(r'^[\w .,!?#$%^&*()-+=/\]+$|^[\w .,!?#$%^&*()-+=/а-яёА-ЯЁ]+$', new_nick):
                await message.reply("Никнейм может содержать только латинские/русские буквы, "
                                    "цифры и базовые символы пунктуации.")
                return

        if '@' in new_nick or validators.url(new_nick) or 't.me' in new_nick:
            await message.reply("Никнейм не может содержать символ '@', ссылки или упоминания t.me.")
            return

        if await is_nickname_taken(new_nick):
            await message.reply("Этот никнейм уже занят. Пожалуйста, выберите другой.")
            return

        try:
            await change_username(user.telegram_id, new_nick)
        except sqlalchemy.exc.IntegrityError as e:
            await message.reply("Этот никнейм уже занят. Пожалуйста, выберите другой.")
            return
        await message.reply(f"Ваш никнейм был изменен на {new_nick}.")
    else:
        await message.reply("Никнейм не может быть пустым. Укажите значение после команды.")


@text_triggers_router.message(F.text.casefold().startswith("промо".casefold()))
async def activate_promo(message: types.Message, dialog_manager: DialogManager):
    promocode = message.text.casefold().split('промо'.casefold(), 1)[1].strip()
    promo = await get_promo(promocode)
    if promo is None:
        await message.answer("Промокод не найден")
        return
    if promo.is_expiated_counts():
        await message.answer("Количество активаций промокода превышено.")
        return
    if promo.is_expiated_time():
        await message.answer("Промокод истек.")
        return
    try:
        channel_member = await message.bot.get_chat_member(promo.channel_id, message.from_user.id)
    except Exception:
        await message.answer("Возникла ошибки при проверке подписки на канал спонсора")
    if channel_member.status not in ["creator", "administrator", "member", "restricted"]:
        await message.answer("Вы не подписаны на канал спонсора, подпишитесь",
                             reply_markup=InlineKeyboardBuilder(
                                 InlineKeyboardButton(text="Канал спонсора", url=promo.link)
                             ).as_markup())
        return
    user = await get_user(message.from_user.id)
    if user.check_promo_expired(promocode):
        await message.answer("Вы уже использовали этот промокод")
        return
    try:
        await promo_use(user.telegram_id, promo)
        await message.answer("Промокод активирован успешно")
    except IsAlreadyResetException:
        await message.answer("Таймер уже на нуле, заберите карточку, а затем активируйте промокод.")


@text_triggers_router.my_chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
async def on_bot_added(update: ChatMemberUpdated):
    if update.chat.type == "private":
        await in_pm_change(update.from_user.id, True)
    elif update.chat.type in ["group", "supergroup"]:
        await in_group_change(update.chat.id, True)
    await update.answer(
        """👋 Добро пожаловать в мир Комару!

🌟 Собирайте уникальные карточки Комару и соревнуйтесь с 
другими игроками.

Как начать:
1. Напишите "Комару" для получения первой карточки.
2. Используйте команду /help 
для информации о доступных командах.

Удачи в нашей вселенной!"""
    )


@text_triggers_router.my_chat_member(ChatMemberUpdatedFilter(IS_MEMBER >> IS_NOT_MEMBER))
async def on_bot_deleted(update: ChatMemberUpdated):
    if update.chat.type == "private":
        await in_pm_change(update.from_user.id, False)
    elif update.chat.type in ["group", "supergroup"]:
        await in_group_change(update.chat.id, False)


def is_nickname_allowed(nickname):
    for symbol in forbidden_symbols:
        if re.search(re.escape(symbol), nickname, re.IGNORECASE):
            return False
    return True


async def random_cat(isPro: bool):
    cats = await get_all_cards()
    random_number = random.randint(1, 95)

    if isPro:
        if 0 <= random_number <= 25:
            eligible_cats = [cat[0] for cat in cats if cat[0].rarity == "Легендарная"]
        elif 26 <= random_number <= 45:
            eligible_cats = [cat[0] for cat in cats if cat[0].rarity == "Мифическая"]
        elif 46 <= random_number <= 65:
            eligible_cats = [cat[0] for cat in cats if cat[0].rarity == "Сверхредкая"]
        elif 66 <= random_number <= 95:
            eligible_cats = [cat[0] for cat in cats if cat[0].rarity == "Редкая"]
    else:
        if 0 <= random_number <= 14:
            eligible_cats = [cat[0] for cat in cats if cat[0].rarity == "Легендарная"]
        elif 15 <= random_number <= 29:
            eligible_cats = [cat[0] for cat in cats if cat[0].rarity == "Мифическая"]
        elif 30 <= random_number <= 49:
            eligible_cats = [cat[0] for cat in cats if cat[0].rarity == "Сверхредкая"]
        elif 50 <= random_number <= 95:
            eligible_cats = [cat[0] for cat in cats if cat[0].rarity == "Редкая"]

    if eligible_cats:
        chosen_cat = random.choice(eligible_cats)
        return chosen_cat
    else:
        return 'чиво'
