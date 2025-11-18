"""
Database Schemas for Pokemon TCG marketplace

Each Pydantic model represents a MongoDB collection. The collection name is the
lowercased class name (e.g., CardListing -> "cardlisting").
"""

from pydantic import BaseModel, Field
from typing import Optional, List

class CardListing(BaseModel):
    """Listings for vintage/forgotten Pokemon TCG singles and collections"""
    name: str = Field(..., description="Card name, e.g., 'Charizard' or 'Base Set Lot'")
    set_name: Optional[str] = Field(None, description="Set name, e.g., 'Base Set', 'Jungle'")
    year: Optional[int] = Field(None, ge=1996, le=2030, description="Release year")
    condition: Optional[str] = Field(None, description="Condition descriptor, e.g., LP, NM, HP")
    rarity: Optional[str] = Field(None, description="Rarity or special tag")
    language: Optional[str] = Field("EN", description="Card language")
    price: float = Field(..., ge=0, description="Listing price in USD")
    images: List[str] = Field(default_factory=list, description="Image URLs")
    description: Optional[str] = Field(None, description="Short description of the item")
    is_collection: bool = Field(False, description="True if this is a multi-card lot/collection")
    featured: bool = Field(False, description="Whether to highlight on homepage")

class Inquiry(BaseModel):
    """Buyer/Seller inquiry form submissions"""
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Contact email")
    intent: str = Field(..., description="'buy' or 'sell'")
    message: str = Field(..., description="Details about what they want to buy/sell")
    target_listing_id: Optional[str] = Field(None, description="If referencing a specific listing")
