from pydantic import BaseModel, Field
from typing import Optional
from app.models.address_pool import Currency
from app.models.request import RequestStatus

class RequestCreate(BaseModel):
    currency: Currency
    payout_address: str = Field(min_length=5)
    contact: Optional[str] = None

class RequestOut(BaseModel):
    id: str
    currency: Currency
    payout_address: str
    contact: str | None
    allocated_address: str | None
    status: RequestStatus

    class Config:
        from_attributes = True