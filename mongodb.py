from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager
from fastapi import FastAPI

class MongoDB:
    def __init__(self, uri: str, db_name: str):
        self.client = AsyncIOMotorClient(uri)
        self.db = self.client[db_name]

    def get_db(self):
        return self.db

    async def close(self):
        self.client.close()

mongodb = MongoDB("mongodb://localhost:27017", "exp_dev_database")

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await mongodb.close()