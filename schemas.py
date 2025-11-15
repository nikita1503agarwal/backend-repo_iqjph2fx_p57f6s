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

from pydantic import BaseModel, Field
from typing import Optional, List

# Example schemas (replace with your own):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
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

# Katana-specific product schema
class Katana(BaseModel):
    """
    Katana products schema
    Collection name: "katana" (lowercase of class name)
    """
    name: str = Field(..., description="Katana name")
    description: str = Field(..., description="Detailed description")
    price: float = Field(..., ge=0, description="Price in USD")
    steel: str = Field(..., description="Blade steel type")
    length_cm: float = Field(..., ge=0, description="Blade length in centimeters")
    weight_kg: Optional[float] = Field(None, ge=0, description="Weight in kilograms")
    images: List[str] = Field(default_factory=list, description="Image URLs")
    stock: int = Field(0, ge=0, description="Available stock")
    rating: Optional[float] = Field(None, ge=0, le=5, description="Average rating")

class OrderItem(BaseModel):
    product_id: str = Field(..., description="ID of the katana product")
    name: str = Field(..., description="Product name snapshot")
    quantity: int = Field(..., ge=1, description="Quantity ordered")
    price: float = Field(..., ge=0, description="Unit price at time of order")
    subtotal: float = Field(..., ge=0, description="quantity * price")

class Order(BaseModel):
    """
    Orders collection schema
    Collection name: "order"
    """
    customer_name: str = Field(..., description="Customer full name")
    email: str = Field(..., description="Customer email")
    address: str = Field(..., description="Shipping address")
    items: List[OrderItem] = Field(..., description="Items in the order")
    total_amount: float = Field(..., ge=0, description="Total order amount")

# Add your own schemas here:
# --------------------------------------------------

# Note: The Flames database viewer will automatically:
# 1. Read these schemas from GET /schema endpoint
# 2. Use them for document validation when creating/editing
# 3. Handle all database operations (CRUD) directly
# 4. You don't need to create any database endpoints!
