from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal
from app.schemas.request import RequestCreate, RequestOut
from app.services.request_service import create_request, get_request, expire_request_if_needed
from app.notify.telegram import notify_new_request

router = APIRouter(prefix="/requests", tags=["requests"])

async def get_session():
    async with AsyncSessionLocal() as session:
        yield session

@router.post("/", response_model=RequestOut, status_code=201)
async def create_request_endpoint(payload: RequestCreate, session: AsyncSession = Depends(get_session)):
    req = await create_request(session, payload.currency, payload.payout_address, payload.contact)
    if not req.allocated_address:
        raise HTTPException(status_code=409, detail="No free addresses for selected currency")
    try:
        await notify_new_request(req)
    except Exception:
        pass
    return req


@router.get("/{request_id}", response_model=RequestOut)
async def get_request_endpoint(request_id: str, session: AsyncSession = Depends(get_session)):
    req = await get_request(session, request_id)
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    await expire_request_if_needed(session, req)
    return req