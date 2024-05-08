from typing import Optional
from fastapi import HTTPException, Depends
from motor.motor_asyncio import AsyncIOMotorClient

from config import settings
from config.oauth import get_current_user

from blogmax.models import User

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


async def update_document(collection_name: str, id: str, data: dict, current_user: User):
    collection = await get_collection(collection_name)
    blog = await collection.find_one({"_id": id})
    if not blog:
        raise HTTPException(status_code=404, detail="Document not found")
    if blog["author"]["_id"] != current_user.get("_id"):
        raise HTTPException(status_code=401, detail="You are not authorized to update this blog")
    await collection.update_one({"_id": id}, {"$set": data})
    updated_blog = await collection.find_one({"_id": id})
    return updated_blog


async def delete_document(collection_name: str, id: str, current_user: User):
    print("????", current_user.get("_id"))
    collection = await get_collection(collection_name)
    blog = await collection.find_one({"_id": id})
    if not blog:
        raise HTTPException(status_code=404, detail="Document not found")
    if blog["author"]["_id"] != current_user.get("_id"):
        raise HTTPException(status_code=401, detail="You are not authorized to delete this blog")
    await collection.delete_one({"_id": id})
    return HTTPException(status_code=204, detail="Document deleted")
