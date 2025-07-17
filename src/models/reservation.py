from pydantic import BaseModel, Field
from typing import Literal

class Reservation(BaseModel):
    reservation_id: str = Field(...)
    guest_id: str = Field(...)
    table_id: str = Field(...)
    menu_id: str = Field(...)
    date: str = Field(...)
    status: Literal['active', 'cancelled'] = 'active'
