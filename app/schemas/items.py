from pydantic import BaseModel, Field

class ItemCreate(BaseModel):
    name: str = Field(..., max_length=100)
    description: str | None = Field(None, max_length=255)

class ItemRead(BaseModel):
    id: int
    name: str
    description: str | None

    class Config:
        from_attributes = True
