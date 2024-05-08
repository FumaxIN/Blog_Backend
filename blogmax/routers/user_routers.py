from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from fastapi.encoders import jsonable_encoder

from typing import Annotated
from config.oauth import get_current_user

from utils.motor_utilities import get_collection
from ..models import User, UpdateUser, Follow

router = APIRouter()


# ----------------- User -----------------
@router.get("/me", response_description="Retrieve current user")
async def read_users_me(
        current_user: Annotated[User, Depends(get_current_user)]
):
    return current_user


@router.put("/me", response_description="Update current user")
async def update_users_me(
        current_user: Annotated[User, Depends(get_current_user)],
        data: UpdateUser = None,
):
    user_collection = await get_collection("users")

    if data.username is not None and data.username != current_user.username:
        if await user_collection.find_one({"username": data.username}):
            raise HTTPException(status_code=400, detail="Username already exists")

    update_user = await user_collection.update_one(
        {"_id": current_user["_id"]},
        {"$set": data.dict(exclude_unset=True)}
    )

    if update_user.modified_count == 0:
        raise HTTPException(status_code=400, detail="No user updated")

    updated_user = await user_collection.find_one({"_id": current_user["_id"]})
    return updated_user


@router.put("/tags/add", response_description="Add tags to current user")
async def add_tags_to_user(
        current_user: Annotated[User, Depends(get_current_user)],
        tags: list[str]
):
    user_collection = await get_collection("users")
    update_user = await user_collection.update_one(
        {"_id": current_user["_id"]},
        {"$addToSet": {"tags": {"$each": tags}}}
    )

    if update_user.modified_count == 0:
        raise HTTPException(status_code=400, detail="No user updated")

    updated_user = await user_collection.find_one({"_id": current_user["_id"]})
    return updated_user


@router.put("/tags/remove", response_description="Remove tags from current user")
async def remove_tags_from_user(
        current_user: Annotated[User, Depends(get_current_user)],
        tags: list[str]
):
    user_collection = await get_collection("users")
    update_user = await user_collection.update_one(
        {"_id": current_user["_id"]},
        {"$pull": {"tags": {"$in": tags}}}
    )

    if update_user.modified_count == 0:
        raise HTTPException(status_code=400, detail="No user updated")

    updated_user = await user_collection.find_one({"_id": current_user["_id"]})
    return updated_user


@router.put("/follow", response_description="Follow a user")
async def follow_user(
        username: str,
        current_user: User = Depends(get_current_user)
):
    user_collection = await get_collection("users")
    user = await user_collection.find_one({"username": username})

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    follow_collection = await get_collection("follows")
    if await follow_collection.find_one({"follower._id": current_user["_id"], "following._id": user["_id"]}):
        raise HTTPException(status_code=400, detail="Already following user")

    follow = Follow(follower=current_user, following=user)
    await follow_collection.insert_one(jsonable_encoder(follow))

    return {"status": "Followed"}
