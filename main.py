from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from contextlib import asynccontextmanager
from bson import ObjectId

# MongoDB configuration
MONGO_URI = "mongodb+srv://aj123:aj123@shoppify.fsyemvp.mongodb.net/"
DATABASE_NAME = "db_example"

# FastAPI app
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    mongo_client = AsyncIOMotorClient(MONGO_URI)
    db = mongo_client[DATABASE_NAME]
    app.state.db = db  # Attach the database to app.state
    print("Connected to MongoDB")
    yield
    # Shutdown logic
    await mongo_client.close()
    print("MongoDB connection closed")

app = FastAPI(lifespan=lifespan)

# Example data model
class Item(BaseModel):
    name: str
    description: str
    price: float

# Example route to create an item
@app.post("/items/")
async def create_item(item: Item):
    item_data = item.model_dump()  # Use model_dump instead of dict
    result = await app.state.db["items"].insert_one(item_data)
    return {"id": str(result.inserted_id), "message": "Item created successfully"}

# Example route to get an item by ID
@app.get("/items/{item_id}")
async def read_item(item_id: str):
    item = await app.state.db["items"].find_one({"_id": ObjectId(item_id)})
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    item["_id"] = str(item["_id"])  # Convert ObjectId to string for response
    return item
