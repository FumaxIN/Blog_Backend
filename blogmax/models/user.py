import random
import string
from datetime import datetime

from pydantic import BaseModel as PydanticBaseModel, Field, constr
from essentials.basemodel import BaseModel


class User(BaseModel):
    username: constr(max_length=10) = Field(...)
    email: constr(max_length=100) = Field(...)
    first_name: constr(max_length=100) = Field(...)
    last_name: constr(max_length=100) = Field(...)
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

    class Login(BaseModel):
        username: constr(max_length=10) = Field(...)
        password: constr(max_length=100) = Field(...)

        class Config:
            populate_by_name = True
            json_schema_extra = {
                "example": {
                    "username": "johndoe",
                    "password": "password",
                }
            }

    class Token(BaseModel):
        access_token: str
        token_type: str

        class Config:
            populate_by_name = True
            json_schema_extra = {
                "example": {
                    "access_token": "string",
                    "token_type": "bearer",
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
