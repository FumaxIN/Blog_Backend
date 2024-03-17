from fastapi import APIRouter, status, Body, Request, Header, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2

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
async def read_user(authorization: str = Header(...)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header is missing")

    if not authorization.startswith("Bearer"):
        raise HTTPException(status_code=401, detail="Invalid authorization header format")

    token = authorization.split(" ")[1]
    # print(token)
    user = await get_current_user(token)
    user_id = user.id
    print(user_id)

    user = await read_document("users", str(user_id))
    return user
