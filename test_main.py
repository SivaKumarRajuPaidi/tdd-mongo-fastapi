import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from bson import ObjectId
from main import app, db
from motor.motor_asyncio import AsyncIOMotorClient
from httpx import AsyncClient, ASGITransport

@pytest.fixture(scope="module")
async def test_db():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    test_db = client.exp_test_database
    yield test_db
    client.drop_database("exp_test_database")

@pytest.fixture
async def async_client(test_db):
    app.dependency_overrides[db] = lambda: test_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    del app.dependency_overrides[db]

@pytest.mark.asyncio(loop_scope="module")
async def test_create_item(async_client):
    response = await async_client.post("/items/", json={"name": "Item 1", "description": "Description 1"})
    assert response.status_code == 200
    data = response.json()
    assert "id" in data

@pytest.mark.asyncio(loop_scope="module")
async def test_read_item(async_client):
    item_id = str(ObjectId())
    await db.items.insert_one({"_id": ObjectId(item_id), "name": "Item 2", "description": "Description 2"})
    response = await async_client.get(f"/items/{item_id}")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert data["name"] == "Item 2"
    assert "description" in data
    assert data["description"] == "Description 2"
    assert "_id" in data
    assert data["_id"] == item_id

@pytest.mark.asyncio(loop_scope="module")
async def test_read_nonexistent_item(async_client):
    invalid_id = str(ObjectId())
    response = await async_client.get(f"/items/{invalid_id}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found"}