from fastapi import APIRouter, Depends, BackgroundTasks
from fastapi.exceptions import HTTPException
from fastapi.encoders import jsonable_encoder

from typing import Annotated
from config.oauth import get_current_user

from utils.motor_utilities import get_collection
from utils.notify import send_follow_notification
from ..models import User, UpdateUser, Follow, UpdateTags

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
        data: UpdateTags
):
    user_collection = await get_collection("users")
    update_user = await user_collection.update_one(
        {"_id": current_user["_id"]},
        {"$addToSet": {"tags": {"$each": data.tags}}}
    )

    if update_user.modified_count == 0:
        raise HTTPException(status_code=400, detail="No user updated")

    updated_user = await user_collection.find_one({"_id": current_user["_id"]})
    return updated_user


@router.put("/tags/remove", response_description="Remove tags from current user")
async def remove_tags_from_user(
        current_user: Annotated[User, Depends(get_current_user)],
        data: UpdateTags
):
    user_collection = await get_collection("users")
    update_user = await user_collection.update_one(
        {"_id": current_user["_id"]},
        {"$pull": {"tags": {"$in": data.tags}}}
    )

    if update_user.modified_count == 0:
        raise HTTPException(status_code=400, detail="No user updated")

    updated_user = await user_collection.find_one({"_id": current_user["_id"]})
    return updated_user


@router.post("/follow", response_description="Follow a user")
async def follow_user(
        background_tasks: BackgroundTasks,
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

    background_tasks.add_task(send_follow_notification, follow.dict())

    return {"status": "Followed"}


@router.post("/unfollow", response_description="Unfollow a user")
async def unfollow_user(
        username: str,
        current_user: User = Depends(get_current_user)
):
    user_collection = await get_collection("users")
    user = await user_collection.find_one({"username": username})

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    follow_collection = await get_collection("follows")
    follow = await follow_collection.find_one({"follower._id": current_user["_id"], "following._id": user["_id"]})

    if not follow:
        raise HTTPException(status_code=400, detail="Not following user")

    await follow_collection.delete_one({"_id": follow["_id"]})

    return {"status": "Unfollowed"}


@router.delete("/me", response_description="Delete current user")
async def delete_users_me(
        current_user: Annotated[User, Depends(get_current_user)]
):
    user_collection = await get_collection("users")
    await user_collection.delete_one({"_id": current_user["_id"]})

    return {"status": "Deleted"}
