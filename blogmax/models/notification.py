import random
import string
from pydantic import Field, constr, BaseModel as PydanticBaseModel
from utils.basemodel import BaseModel

from .user import User


class Notification(BaseModel):
    title: constr(max_length=100) = Field(...)
    content: constr(max_length=100000) = Field(...)
    redirect_url: str | None = Field(None)
    user: User
    read: bool = Field(default=False)

    class Config:
        populate_by_name = True


