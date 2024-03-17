from fastapi import APIRouter, Depends

from typing import Annotated
from config.oauth import get_current_user

from ..models import User

router = APIRouter()


# ----------------- User -----------------
@router.get("/me", response_description="Retrieve current user")
async def read_users_me(
        current_user: Annotated[User, Depends(get_current_user)]
):
    return current_user
