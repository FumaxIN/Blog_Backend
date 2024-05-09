import random
import string
from datetime import datetime

from pydantic import BaseModel as PydanticBaseModel, Field, constr, field_validator, root_validator
from utils.basemodel import BaseModel


class User(BaseModel):
    username: constr(max_length=10) = Field(...)
    email: constr(max_length=100) = Field(...)
    first_name: constr(max_length=100) = Field(...)
    last_name: constr(max_length=100) = Field(...)
    tags: list[str] = Field(default_factory=list)
    password: constr(max_length=100) = Field(...)

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "username": "johndoe",
                "email": "johndoe@gmail.com",
                "first_name": "John",
                "last_name": "Doe",
                "password": "password",
            }
        }


class UpdateUser(BaseModel):
    username: str | None = None
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "email": "johndoe@gmail.com",
                "first_name": "John",
                "last_name": "Doe",
                "tags": ["tag1", "tag2"],
            }
        }

class UpdateTags(BaseModel):
    tags: list[str]

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "tags": ["tag1", "tag2"],
            }
        }

class TokenData(BaseModel):
    username: str = None

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "username": "johndoe",
            }
        }


class Follow(BaseModel):
    follower: User
    following: User

    class Config:
        populate_by_name = True
