from fastapi import APIRouter, Request, Depends
from typing import Annotated, List
from collections import Counter
from config.oauth import get_current_user

from ..models import User
from utils.motor_utilities import (
    read_collection,
)

router = APIRouter()


def calculate_tag_similarity(user_tags: List[str], blog_tags: List[str]) -> int:
    user_tag_counter = Counter(user_tags)
    blog_tag_counter = Counter(blog_tags)
    common_tags = user_tag_counter & blog_tag_counter
    return sum(common_tags.values())


# ----------------- Blog by User's tags preference -----------------
@router.get("/blogs", response_description="List all blogs by user's tags preference")
async def list_blogs_by_user_tags(request: Request, current_user: Annotated[User, Depends(get_current_user)]):
    all_blogs = await read_collection("blogs")

    blogs_with_scores = [(blog, calculate_tag_similarity(current_user.get("tags"), blog.get("tags"))) for blog in all_blogs]

    sorted_blogs = sorted(blogs_with_scores, key=lambda x: x[1], reverse=True)
    sorted_blog_objects = [blog for blog, _ in sorted_blogs]

    return sorted_blog_objects



