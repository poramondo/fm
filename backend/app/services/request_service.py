from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.config import settings
from app.models.request import Request, RequestStatus
from app.models.address_pool import Currency
from .address_service import allocate_address, release_address

async def create_request(session: AsyncSession, currency: Currency, payout_address: str, contact: str | None) -> Request:
    req = Request(currency=currency, payout_address=payout_address, contact=contact)
    req.created_at = datetime.utcnow()
    req.expires_at = req.created_at + timedelta(minutes=settings.ADDRESS_HOLD_MINUTES)

    session.add(req)
    await session.flush()  # получаем req.id

    allocated = await allocate_address(session, currency, req.id)
    if not allocated:
        # нет свободных адресов — оставим без allocated_address
        req.status = RequestStatus.NEW
    else:
        req.allocated_address = allocated
        req.status = RequestStatus.AWAITING_PAYMENT

    await session.commit()
    await session.refresh(req)
    return req

async def get_request(session: AsyncSession, request_id: str) -> Request | None:
    q = select(Request).where(Request.id == request_id)
    res = await session.execute(q)
    return res.scalar_one_or_none()

async def expire_request_if_needed(session: AsyncSession, request: Request):
    if request.expires_at and request.status in {RequestStatus.NEW, RequestStatus.AWAITING_PAYMENT}:
        if datetime.utcnow() > request.expires_at:
            request.status = RequestStatus.EXPIRED
            await release_address(session, request.id)
            await session.commit()
            await session.refresh(request)