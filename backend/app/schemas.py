from pydantic import BaseModel
from typing import List


class BillItemCreate(BaseModel):
    item_name: str
    quantity: int
    rate: int

class BillCreate(BaseModel):
    customer_name: str
    items: List[BillItemCreate]

class BillCreate(BaseModel):
    factory_id: int
    items: list[BillItemCreate]

class UserCreate(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class ForgotPassword(BaseModel):
    email: str


class ResetPassword(BaseModel):
    new_password: str

class FactoryCreate(BaseModel):
    name: str
    address: str | None = None


class FactoryResponse(BaseModel):
    id: int
    name: str
    address: str | None = None

    class Config:
        from_attributes = True


class BillResponse(BaseModel):
    id: int
    factory_id: int
    description: str
    amount: int

    class Config:
        from_attributes = True


class BillItemResponse(BaseModel):
    id: int
    item_name: str
    quantity: int
    rate: int
    total: int

    class Config:
        from_attributes = True

class BillUpdate(BaseModel):
    items: list[BillItemCreate]
