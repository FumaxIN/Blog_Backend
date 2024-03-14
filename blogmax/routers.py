from fastapi import APIRouter, Depends, HTTPException, status, Body, Request
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

# import models
from .models import Blog

router = APIRouter()


@router.post("/", response_description="Add new blog", response_model=Blog)
async def create_blog(request: Request, blog: Blog = Body(...)):
    blog = jsonable_encoder(blog)
    new_blog = await request.app.mongodb["blogmax"]["blogs"].insert_one(blog)
    created_blog = await request.app.mongodb["blogmax"]["blogs"].find_one({"_id": new_blog.inserted_id})
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_blog)
