import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Katana, Order, OrderItem

app = FastAPI(title="Katana Shop API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Katana Shop Backend is running"}

# Helper to convert Mongo documents for JSON
class JSONModel(BaseModel):
    class Config:
        arbitrary_types_allowed = True


def serialize_doc(doc: dict):
    if not doc:
        return doc
    d = dict(doc)
    if "_id" in d:
        d["id"] = str(d.pop("_id"))
    return d

# Seed some demo katanas if collection empty
@app.on_event("startup")
async def seed_katanas():
    try:
        if db is None:
            return
        if db.katana.count_documents({}) == 0:
            samples = [
                {
                    "name": "Hattori Hanzo Classic",
                    "description": "Hand-forged T10 steel with clay tempering.",
                    "price": 899.0,
                    "steel": "T10",
                    "length_cm": 73.0,
                    "weight_kg": 1.2,
                    "images": ["https://images.unsplash.com/photo-1610248381701-4b4e8a5fb50a"],
                    "stock": 5,
                    "rating": 4.8,
                },
                {
                    "name": "Dragon's Breath",
                    "description": "Folded Damascus steel, ornate tsuba.",
                    "price": 1299.0,
                    "steel": "Damascus",
                    "length_cm": 72.4,
                    "weight_kg": 1.25,
                    "images": ["https://images.unsplash.com/photo-1593808282301-8d3b0e3b60c1"],
                    "stock": 3,
                    "rating": 4.9,
                },
                {
                    "name": "Shinobi Light",
                    "description": "Spring steel, agile and resilient.",
                    "price": 499.0,
                    "steel": "5160",
                    "length_cm": 70.0,
                    "weight_kg": 1.05,
                    "images": ["https://images.unsplash.com/photo-1519681393784-d120267933ba"],
                    "stock": 10,
                    "rating": 4.6,
                },
            ]
            for s in samples:
                create_document("katana", s)
    except Exception:
        pass

@app.get("/api/katanas")
def list_katanas(limit: int = 50):
    try:
        docs = get_documents("katana", {}, limit)
        return [serialize_doc(d) for d in docs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class CreateOrderPayload(BaseModel):
    customer_name: str
    email: str
    address: str
    items: List[OrderItem]

@app.post("/api/orders")
def create_order(payload: CreateOrderPayload):
    try:
        # compute totals and validate stock
        total = 0.0
        for item in payload.items:
            total += item.price * item.quantity
        order_doc = Order(
            customer_name=payload.customer_name,
            email=payload.email,
            address=payload.address,
            items=[OrderItem(**i.model_dump()) for i in payload.items],
            total_amount=total,
        ).model_dump()
        order_id = create_document("order", order_doc)
        return {"id": order_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        from database import db as _db
        if _db is not None:
            response["database"] = "✅ Connected & Working"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = _db.name if hasattr(_db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = _db.list_collection_names()
                response["collections"] = collections[:10]
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
