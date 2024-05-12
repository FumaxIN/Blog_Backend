from fastapi import APIRouter, status, Body, Request, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from typing import Annotated
from config.oauth import get_current_user

from ..models import Blog, BlogUpdate, BlogInDB, User, Like
from utils.motor_utilities import (
    get_collection,
    create_document,
    read_collection,
    read_document,
    update_document,
    delete_document
)
from utils.notify import send_blog_notification, send_like_notification

router = APIRouter()


# ----------------- Blog -----------------
@router.post("", response_description="Add new blog")
async def create_blog(request: Request, background_tasks: BackgroundTasks, blog: Blog = Body(...), author: User = Depends(get_current_user)):
    blog_data = blog.dict()
    blog_data["_id"] = str(blog_data["id"])
    blog_in_db = BlogInDB(**blog_data, author=author)
    background_tasks.add_task(send_blog_notification, blog_in_db.dict(), author)
    response = await create_document("blogs", jsonable_encoder(blog_in_db))

    return JSONResponse(status_code=status.HTTP_201_CREATED, content=response)


@router.get("", response_description="List all blogs", response_model=dict)
async def list_blogs(
        request: Request, title: str = "", content: str = "", author: str = "", tag: str = "", skip: int = 0, limit: int = 10
):
    queries = {}
    if title:
        queries["title"] = {"$regex": title, "$options": "i"}
    if content:
        queries["content"] = {"$regex": content, "$options": "i"}
    if author:
        queries["author.username"] = {"$regex": author, "$options": "i"}
    if tag:
        queries["tags"] = {"$in": [tag]}

    return await read_collection(
        "blogs",
        queries,
        skip,
        limit
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


@router.post("/{id}/like", response_description="Like a blog")
async def like_blog(
        background_tasks: BackgroundTasks,
        id: str,
        current_user: Annotated[User, Depends(get_current_user)]
):
    try:
        blog_collection = await get_collection("blogs")
        blog_doc = await blog_collection.find_one({"_id": id})

        likes = await get_collection("likes")
        liked = await likes.find_one({"liker._id": current_user["_id"], "blog._id": id})
        if liked:
            await likes.delete_one({"_id": liked["_id"]})
            await blog_collection.update_one({"_id": id}, {"$inc": {"likes": -1}})
            return JSONResponse(status_code=status.HTTP_200_OK, content={"status": "Unliked"})
        else:
            blog = BlogInDB(**blog_doc)
            like = Like(liker=current_user, blog=blog)
            await create_document("likes", jsonable_encoder(like))
            await blog_collection.update_one({"_id": id}, {"$inc": {"likes": 1}})
            background_tasks.add_task(send_like_notification, like.dict(), blog.author)
            return JSONResponse(status_code=status.HTTP_201_CREATED, content={"status": "Liked"})
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(e)})


@router.get("/{id}/liked_by", response_description="List users who liked the blog")
async def liked_by(id: str, skip: int = 0, limit: int = 10):
    try:
        likes = await get_collection("likes")
        liked = await likes.find({"blog._id": id}, skip=skip, limit=limit).to_list(limit)
        return liked
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(e)})
