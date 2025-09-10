import asyncio
from datetime import datetime, timedelta
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.request import Request, RequestStatus
from app.core.config import settings
from app.services.address_service import release_address

async def run_cleanup():
    async with AsyncSessionLocal() as session:
        # 1) Истёкшие — помечаем EXPIRED и освобождаем адрес
        now = datetime.utcnow()
        q = select(Request).where(Request.status.in_([RequestStatus.NEW, RequestStatus.AWAITING_PAYMENT]))
        res = await session.execute(q)
        for req in res.scalars().all():
            if req.expires_at and now > req.expires_at:
                req.status = RequestStatus.EXPIRED
                await release_address(session, req.id)
        await session.commit()

        # 2) Удаляем записи старше TTL
        ttl_delta = timedelta(hours=settings.LOG_TTL_HOURS)
        cutoff = now - ttl_delta
        q2 = select(Request).where(Request.created_at < cutoff)
        res2 = await session.execute(q2)
        to_delete = res2.scalars().all()
        for r in to_delete:
            await release_address(session, r.id)
            await session.delete(r)
        await session.commit()

if __name__ == "__main__":
    asyncio.run(run_cleanup())