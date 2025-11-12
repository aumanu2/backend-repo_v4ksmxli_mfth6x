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

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict

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

# White Circle Website data models

class Metric(BaseModel):
    label: str
    value: str

class CaseStudy(BaseModel):
    """
    Marketing case studies
    Collection: "casestudy"
    """
    brand: str = Field(..., description="Brand name")
    logo_url: Optional[HttpUrl] = Field(None, description="URL to brand logo")
    industry: str = Field(..., description="Industry vertical")
    scope: List[str] = Field(default_factory=list, description="Scope/services involved")
    campaign_type: str = Field(..., description="Organic, Paid, Integrated, etc.")
    headline: str = Field(..., description="Short headline for the result")
    highlight: str = Field(..., description="One-line highlight")
    metrics: List[Metric] = Field(default_factory=list, description="Key metrics like ROAS, Reach, Engagement")
    tags: List[str] = Field(default_factory=list, description="Searchable tags")
    video_url: Optional[HttpUrl] = Field(None, description="Optional background video")
    featured: bool = Field(False, description="Whether to feature on homepage")
    performance_score: Optional[float] = Field(None, description="Optional performance score for sorting")

# Add your own schemas here:
# --------------------------------------------------

# Note: The Flames database viewer will automatically:
# 1. Read these schemas from GET /schema endpoint
# 2. Use them for document validation when creating/editing
# 3. Handle all database operations (CRUD) directly
# 4. You don't need to create any database endpoints!
