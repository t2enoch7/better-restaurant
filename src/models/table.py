from pydantic import BaseModel, Field

class Table(BaseModel):
    table_id: str = Field(...)
    capacity: int = Field(..., gt=0)
    location: str = Field(...)
