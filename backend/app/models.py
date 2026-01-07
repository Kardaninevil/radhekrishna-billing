from sqlalchemy import Column, Integer, String
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)

class Factory(Base):
    __tablename__ = "factories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=True)

class Bill(Base):
    __tablename__ = "bills"

    id = Column(Integer, primary_key=True, index=True)
    factory_id = Column(Integer, nullable=False)
    description = Column(String, nullable=False)
    amount = Column(Integer, nullable=False)
    gst_enabled = Column(Integer, default=0)  # 0 = OFF, 1 = ON
    gst_percent = Column(Integer, default=18)


class BillItem(Base):
    __tablename__ = "bill_items"

    id = Column(Integer, primary_key=True, index=True)
    bill_id = Column(Integer, nullable=False)
    item_name = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    rate = Column(Integer, nullable=False)
    total = Column(Integer, nullable=False)
