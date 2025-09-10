from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.address_pool import AddressPool, Currency

async def allocate_address(session: AsyncSession, currency: Currency, request_id: str) -> str | None:
    # Берём первый свободный адрес по валюте
    q = (
        select(AddressPool)
        .where(AddressPool.currency == currency, AddressPool.is_allocated == False)  # noqa: E712
        .limit(1)
        .with_for_update(skip_locked=True)
    )
    res = await session.execute(q)
    addr: AddressPool | None = res.scalar_one_or_none()
    if not addr:
        return None
    addr.is_allocated = True
    addr.allocated_at = datetime.utcnow()
    addr.request_id = request_id
    return addr.address

async def release_address(session: AsyncSession, request_id: str):
    q = select(AddressPool).where(AddressPool.request_id == request_id)
    res = await session.execute(q)
    addr = res.scalar_one_or_none()
    if addr:
        addr.is_allocated = False
        addr.allocated_at = None
        addr.request_id = None