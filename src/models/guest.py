from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class Guest(BaseModel):
    guest_id: str = Field(...)
    name: str = Field(..., min_length=1)
    email: EmailStr
    phone: str = Field(..., min_length=7)
