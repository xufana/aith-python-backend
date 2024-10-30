from pydantic import BaseModel, Field
from typing import Optional

class CartItem(BaseModel):
    id: int
    name: str
    quantity: int
    avaliable: bool = Field(default=False)

class Cart(BaseModel):
    id: int
    items: Optional[list[CartItem]] = None
    price: Optional[float] = None