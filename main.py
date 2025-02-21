from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from bson import ObjectId
from mongodb import lifespan, mongodb

app = FastAPI(lifespan=lifespan)

def get_db():
    return mongodb.get_db()

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
