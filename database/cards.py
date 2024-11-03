import json

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from utils.loader import engine
from .models import Card


async def parse_cards(filename):
    async with AsyncSession(engine) as session:
        with open(filename, 'r', encoding="utf8") as f:
            date = json.load(f)
            date = date['cats']
            for card in date:
                card_id = int(card['id'])
                name = card['name']
                points = int(card['points'])
                rarity = card['rarity']
                photo = card['photo']
                db_card = Card(id=card_id, name=name, points=points, rarity=rarity, photo=photo)
                session.add(db_card)
        await session.commit()


async def get_card(card_id: int):
    async with AsyncSession(engine) as session:
        card: Card = (await session.execute(select(Card).where(Card.id == card_id))).scalar_one_or_none()
        return card


async def get_all_cards():
    async with AsyncSession(engine) as session:
        cards: [Card] = (await session.execute(select(Card))).all()
        return cards
