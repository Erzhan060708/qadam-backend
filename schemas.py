from pydantic import BaseModel, EmailStr
from typing import Optional, List

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class StoreCreate(BaseModel):
    name: str
    address: str
    phone: Optional[str] = None
    working_hours: Optional[str] = "09:00 - 22:00"
    category: Optional[str] = "Кафе"
    rating: Optional[float] = 4.5
    image_url: Optional[str] = None

class BagCreate(BaseModel):
    store_id: int
    title: str
    description: Optional[str] = None
    original_price: float
    discounted_price: float
    pickup_start: str
    pickup_end: str
    quantity_available: int = 1
    image_url: Optional[str] = None

class OrderCreate(BaseModel):
    bag_id: int