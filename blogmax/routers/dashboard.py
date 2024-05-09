from fastapi import APIRouter, Request, Depends
from typing import Annotated, List
from collections import Counter
from config.oauth import get_current_user

from ..models import User, Notification
from utils.motor_utilities import (
    read_collection,
    get_collection
)

router = APIRouter()


def calculate_tag_similarity(user_tags: List[str], blog_tags: List[str]) -> int:
    user_tag_counter = Counter(user_tags)
    blog_tag_counter = Counter(blog_tags)
    common_tags = user_tag_counter & blog_tag_counter
    return sum(common_tags.values())


# ----------------- Blog by User's tags preference -----------------
@router.get("/blogs", response_description="List all blogs by user's tags preference")
async def list_blogs_by_user_tags(
        request: Request, current_user: Annotated[User, Depends(get_current_user)], skip: int = 0, limit: int = 10
):
    all_blogs = await read_collection("blogs", skip=skip, limit=limit)
    print(all_blogs.get("documents"))
    blogs_with_scores = [(blog, calculate_tag_similarity(current_user.get("tags"), blog.get("tags"))) for blog in all_blogs.get("documents")]

    sorted_blogs = sorted(blogs_with_scores, key=lambda x: x[1], reverse=True)
    sorted_blog_objects = [blog for blog, _ in sorted_blogs]

    return sorted_blog_objects


@router.get("/notifications", response_description="List all notifications for current user")
async def list_notifications(
        request: Request, current_user: Annotated[User, Depends(get_current_user)], skip: int = 0, limit: int = 10
):
    return await read_collection("notifications", {"user._id": current_user.get("_id")}, skip, limit)


@router.post("/notifications/read", response_description="Read all unread notifications for current user")
async def read_notifications(
        request: Request, current_user: Annotated[User, Depends(get_current_user)]
):
    notifs = await get_collection("notifications")
    await notifs.update_many({"user._id": current_user.get("_id"), "read": False}, {"$set": {"read": True}})

    return {"message": "All notifications are read"}

@router.get("/notifications/unread", response_description="List all unread notifications for current user")
async def list_unread_notifications(
        request: Request, current_user: Annotated[User, Depends(get_current_user)], skip: int = 0, limit: int = 10
):
    return await read_collection("notifications", {"user._id": current_user.get("_id"), "read": False}, skip, limit)