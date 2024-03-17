from fastapi import APIRouter, status, Body, Request, Header, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2

from typing import Optional, List, Annotated
from config.oauth import get_current_user

from ..models import Blog, BlogInDB, User
from essentials.motor_utilities import (
    create_document,
    read_collection,
    read_document,
    update_document,
    delete_document
)

router = APIRouter()


#----------------- User -----------------
@router.get("/me", response_description="Retrieve current user")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)]
):
    return current_user


