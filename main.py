from fastapi import FastAPI, HTTPException, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from bson import ObjectId

app = FastAPI()

client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client.exp_dev_database

def get_db():
    return db

class Item(BaseModel):
    name: str
    description: str

@app.post("/items/")
async def create_item(item: Item, db = Depends(get_db)):
    result = await db.items.insert_one(item.model_dump())
    return {"id": str(result.inserted_id)}

@app.get("/items/{item_id}")
async def read_item(item_id: str, db = Depends(get_db)):
    item = await db.items.find_one({"_id": ObjectId(item_id)})
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    item["_id"] = str(item["_id"])
    return item
