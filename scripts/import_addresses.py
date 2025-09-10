"""
Запуск внутри контейнера backend, например:
  docker compose run --rm backend python /app/app/../scripts/import_addresses.py

Отредактируйте список ADDRESSES перед запуском.
"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import SessionLocal
from app.models.address_pool import AddressPool, Currency

# >>> ЗАПОЛНИТЕ список адресов <<<
ADDRESSES = {
    "BITCOIN": ["btc_test_addr_1", "btc_test_addr_2"],
    "ETHEREUM": ["eth_test_addr_1"],
    "TRC-20": ["trc_test_addr_1"],
    "ERC-20": ["erc_test_addr_1"],
    "MONERO": ["xmr_test_addr_1"],
}

async def ensure_addresses(session: AsyncSession):
    for cur, items in ADDRESSES.items():
        currency = Currency(cur)
        for a in items:
            # не дублируем
            q = select(AddressPool).where(AddressPool.address == a)
            res = await session.execute(q)
            if res.scalar_one_or_none():
                continue
            session.add(AddressPool(currency=currency, address=a))
    await session.commit()

async def main():
    async with AsyncSessionLocal() as session:
        await ensure_addresses(session)

if __name__ == "__main__":
    asyncio.run(main())