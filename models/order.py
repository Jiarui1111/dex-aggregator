import os, sys
from sqlmodel import SQLModel, Field
from datetime import datetime
import uuid
from .enums import OrderStatus

class Order(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_address: str
    token_in: str
    token_out: str
    amount_in: float
    target_price: float
    expiry_time: datetime
    status: OrderStatus = Field(default=OrderStatus.OPEN)
    created_at: datetime = Field(default_factory=datetime.utcnow)
