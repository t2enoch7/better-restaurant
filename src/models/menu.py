from pydantic import BaseModel, Field

class Menu(BaseModel):
    menu_id: str = Field(...)
    name: str = Field(...)
    description: str = Field(...)
    price: float = Field(..., gt=0)
