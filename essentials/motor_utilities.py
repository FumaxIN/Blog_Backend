from typing import Optional
from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorClient

from config import settings

client = AsyncIOMotorClient(settings.DB_URL)
db = client[settings.DB_NAME]


async def get_collection(collection_name: str):
    collection = db.get_collection(collection_name)
    return collection


async def read_collection(collection_name: str, query: Optional[dict] = None):
    collection = await get_collection(collection_name)
    documents = []

    if query:
        async for document in collection.find(query):
            documents.append(document)
    else:
        async for document in collection.find():
            documents.append(document)

    return documents


async def read_document(collection_name: str, id: str):
    collection = await get_collection(collection_name)
    document = await collection.find_one({"_id": id})
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


async def create_document(collection_name: str, data: dict):
    collection = await get_collection(collection_name)
    document = await collection.insert_one(data)
    inserted_document = await collection.find_one({"_id": document.inserted_id})
    return inserted_document


async def update_document(collection_name: str, id: str, data: dict):
    collection = await get_collection(collection_name)
    result = await collection.update_one({"_id": id}, {"$set": data})
    print(result.matched_count, result.modified_count, result.acknowledged)
    if not result.matched_count:
        raise HTTPException(status_code=404, detail="Document not found")
    document = await collection.find_one({"_id": id})
    return document


async def delete_document(collection_name: str, id: str):
    collection = await get_collection(collection_name)
    deleted_document = await collection.delete_one({"_id": id})
    if not deleted_document:
        raise HTTPException(status_code=404, detail="Document not found")
    return HTTPException(status_code=204, detail="Document deleted")
