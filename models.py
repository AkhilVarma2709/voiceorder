from pydantic import BaseModel
from typing import Optional
from enum import Enum


class OrderStatus(str, Enum):
    new = "new"
    accepted = "accepted"
    ready = "ready"
    completed = "completed"


class StatusUpdate(BaseModel):
    status: OrderStatus


class OrderOut(BaseModel):
    id: str
    restaurant_id: Optional[str] = None
    call_id: Optional[str] = None
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    order_items: Optional[str] = None
    order_total: Optional[float] = None
    special_instructions: Optional[str] = None
    pickup_confirmed: Optional[bool] = False
    call_completed: Optional[bool] = False
    call_summary: Optional[str] = None
    status: Optional[str] = "new"
    created_at: Optional[str] = None
