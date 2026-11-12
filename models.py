from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    role = Column(String, default="customer") # 'customer' немесе 'merchant'
    points = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    orders = relationship("Order", back_populates="user")
    merchant_stores = relationship("Store", foreign_keys="Store.owner_user_id")

class Store(Base):
    __tablename__ = "stores"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    address = Column(String)
    phone = Column(String, nullable=True)
    working_hours = Column(String, default="09:00 - 22:00")
    category = Column(String, default="Кафе")
    rating = Column(Float, default=4.5)
    image_url = Column(String, nullable=True)
    owner_user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    bags = relationship("Bag", back_populates="store")
    owner = relationship("User", foreign_keys=[owner_user_id])
    announcements = relationship("Announcement", back_populates="store", cascade="all, delete-orphan")

class Announcement(Base):
    __tablename__ = "announcements"
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    body = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    store = relationship("Store", back_populates="announcements")

class Bag(Base):
    __tablename__ = "bags"
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"))
    title = Column(String)
    description = Column(String, nullable=True)
    original_price = Column(Float)
    discounted_price = Column(Float)
    pickup_start = Column(String)
    pickup_end = Column(String)
    quantity_available = Column(Integer, default=1)
    status = Column(String, default="active")
    image_url = Column(String, nullable=True)
    
    store = relationship("Store", back_populates="bags")
    orders = relationship("Order", back_populates="bag")

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    bag_id = Column(Integer, ForeignKey("bags.id"))
    qr_code = Column(String, unique=True, index=True)
    request_key = Column(String, nullable=True, unique=True, index=True)
    status = Column(String, default="paid")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="orders")
    bag = relationship("Bag", back_populates="orders")
