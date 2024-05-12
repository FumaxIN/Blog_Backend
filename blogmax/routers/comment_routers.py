from fastapi import APIRouter, status, Body, Request, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from typing import Annotated
from config.oauth import get_current_user

from ..models import Blog, BlogUpdate, BlogInDB, User, Comment,CommentInDB
from utils.motor_utilities import (
    get_collection,
    create_document,
    read_collection,
    read_document,
    update_document,
    delete_document
)
from utils.notify import send_comment_notification

router = APIRouter()


@router.post("/{blog_id}/comments", response_description="Add new comment")
async def create_comment(
        background_tasks: BackgroundTasks,
        blog_id: str,
        commenter: Annotated[User,
        Depends(get_current_user)],
        comment: Comment = Body(...)):
    comment_data = comment.dict()
    blog_collection = await get_collection("blogs")
    blog = await blog_collection.find_one({"_id": blog_id})
    if not blog:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"message": "Blog not found"})
    comment_data["_id"] = str(comment_data["id"])
    comment_in_db = CommentInDB(**comment_data, commenter=commenter, blog=blog)
    response = await create_document("comments", jsonable_encoder(comment_in_db))
    background_tasks.add_task(send_comment_notification, comment_in_db.dict(), blog.get("author"))

    await blog_collection.update_one({"_id": blog_id}, {"$inc": {"comments": 1}})

    return JSONResponse(status_code=status.HTTP_201_CREATED, content=response)


@router.get("/{blog_id}/comments", response_description="List all comments", response_model=dict)
async def list_comments(
        request: Request, blog_id: str, commenter: str = "", skip: int = 0, limit: int = 10
):
    queries = {}
    if blog_id:
        queries["blog._id"] = blog_id
    if commenter:
        queries["commenter.username"] = {"$regex": commenter, "$options": "i"}

    return await read_collection(
        "comments",
        queries,
        skip,
        limit
    )


@router.delete("/comments/{id}", response_description="Delete a comment")
async def delete_comment(id: str, commenter: Annotated[User, Depends(get_current_user)]):
    comments_collection = await get_collection("comments")
    comment = await comments_collection.find_one({"_id": id})
    if not comment:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"message": "Comment not found"})

    if commenter.get("_id") != comment.get("commenter").get("_id"):
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"message": "You are not authorized to delete this comment"})

    await comments_collection.delete_one({"_id": id})

    blog_collection = await get_collection("blogs")
    await blog_collection.update_one({"_id": comment.get("blog_id")}, {"$inc": {"comments": -1}})

    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content={"message": "Comment deleted"})