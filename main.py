import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import CardListing, Inquiry

app = FastAPI(title="Pokemon TCG Vintage Marketplace API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Utility to validate ObjectId strings
class ObjectIdStr(BaseModel):
    id: str

    @property
    def object_id(self) -> ObjectId:
        try:
            return ObjectId(self.id)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid ID format")


@app.get("/")
def read_root():
    return {"message": "Pokemon TCG Vintage Marketplace Backend"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": [],
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, "name") else "❌ Unknown"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"

    return response


# Seed a few featured vintage listings if collection is empty
@app.post("/seed", tags=["admin"])
def seed_listings():
    try:
        existing = db["cardlisting"].count_documents({}) if db else 0
        if existing > 0:
            return {"seeded": False, "message": "Listings already exist"}
        samples = [
            {
                "name": "Base Set Charizard Holo",
                "set_name": "Base Set",
                "year": 1999,
                "condition": "LP",
                "rarity": "Holo Rare",
                "price": 399.0,
                "images": [
                    "https://images.pokemontcg.io/base1/4_hires.png"
                ],
                "description": "Iconic WOTC era Charizard in lightly played condition.",
                "is_collection": False,
                "featured": True,
            },
            {
                "name": "Jungle Set Lot (20 cards)",
                "set_name": "Jungle",
                "year": 1999,
                "condition": "NM/LP mix",
                "rarity": "Mixed",
                "price": 89.0,
                "images": [
                    "https://product-images.tcgplayer.com/fit-in/400x400/228867.jpg"
                ],
                "description": "Assorted commons/uncommons with a few rares.",
                "is_collection": True,
                "featured": True,
            },
            {
                "name": "Neo Genesis Lugia Holo",
                "set_name": "Neo Genesis",
                "year": 2000,
                "condition": "HP",
                "rarity": "Holo Rare",
                "price": 249.0,
                "images": [
                    "https://images.pokemontcg.io/neo1/9_hires.png"
                ],
                "description": "Well-loved copy with creases but great for display.",
                "is_collection": False,
                "featured": True,
            },
        ]
        ids = []
        for s in samples:
            ids.append(create_document("cardlisting", s))
        return {"seeded": True, "count": len(ids), "ids": ids}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Public endpoints
@app.get("/listings", response_model=List[CardListing])
def get_listings(featured: Optional[bool] = None):
    try:
        query = {}
        if featured is not None:
            query["featured"] = featured
        docs = get_documents("cardlisting", query, limit=50)
        # Remove Mongo-specific fields for response
        clean = []
        for d in docs:
            d.pop("_id", None)
            clean.append(d)
        return clean
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class InquiryRequest(BaseModel):
    name: str
    email: str
    intent: str
    message: str
    target_listing_id: Optional[str] = None


@app.post("/inquiries")
def submit_inquiry(payload: InquiryRequest):
    try:
        data = payload.model_dump()
        create_document("inquiry", data)
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
