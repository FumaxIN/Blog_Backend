from fastapi import APIRouter, status, Body, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from typing import Annotated
from config.oauth import get_current_user

from ..models import Blog, BlogUpdate, BlogInDB, User
from utils.motor_utilities import (
    create_document,
    read_collection,
    read_document,
    update_document,
    delete_document
)

router = APIRouter()


# ----------------- Blog -----------------
@router.post("", response_description="Add new blog")
async def create_blog(request: Request, blog: Blog = Body(...), author: User = Depends(get_current_user)):
    blog_data = blog.dict()
    blog_in_db = BlogInDB(**blog_data, author=author)
    response = await create_document("blogs", jsonable_encoder(blog_in_db))
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=response)


@router.get("", response_description="List all blogs", response_model=list[BlogInDB])
async def list_blogs(request: Request, title: str = "", content: str = ""):
    return await read_collection(
        "blogs",
        {
            "title": {"$regex": title, "$options": "i"},
            "content": {"$regex": content, "$options": "i"}}
    )


@router.get("/{id}", response_description="Retrieve a blog", response_model=BlogInDB)
async def read(id: str):
    return await read_document("blogs", id)


@router.put("/{id}", response_description="Update a blog")
async def update(id: str, current_user: Annotated[User, Depends(get_current_user)], data: BlogUpdate = None):
    return await update_document("blogs", id, data, current_user)


@router.delete("/{id}", response_description="Delete a blog")
async def delete(id: str, current_user: Annotated[User, Depends(get_current_user)]):
    return await delete_document("blogs", id, current_user)
