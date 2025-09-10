from pydantic import BaseModel
from app.models.address_pool import Currency

class AddressIn(BaseModel):
    currency: Currency
    address: str

class AddressOut(BaseModel):
    id: int
    currency: Currency
    address: str
    is_allocated: bool

    class Config:
        from_attributes = True