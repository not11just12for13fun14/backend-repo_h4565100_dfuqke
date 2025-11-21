"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Literal
from datetime import datetime

# Example schemas (you can keep or remove if not used by your app)
class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address")
    address: Optional[str] = Field(None, description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Barbershop-specific schemas
class Appointment(BaseModel):
    """
    Appointments collection schema
    Collection name: "appointment"
    """
    name: str = Field(..., min_length=2, description="Client full name")
    email: Optional[EmailStr] = Field(None, description="Client email")
    phone: str = Field(..., min_length=7, max_length=20, description="Client phone number")
    date: str = Field(..., description="Requested date (YYYY-MM-DD)")
    time: str = Field(..., description="Requested time (HH:MM)")
    service: str = Field(..., description="Selected service name")
    notes: Optional[str] = Field(None, description="Additional notes")
    status: Literal["pending", "confirmed", "cancelled"] = Field("pending", description="Appointment status")
    preferred_barber: Optional[str] = Field(None, description="Preferred barber if any")
    created_at: Optional[datetime] = Field(None, description="Auto-set on insert")
    updated_at: Optional[datetime] = Field(None, description="Auto-set on update")
