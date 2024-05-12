from pydantic import Field, constr, BaseModel as PydanticBaseModel, model_validator
from utils.basemodel import BaseModel

from .user import User
from .blog import Blog


class Like(BaseModel):
    liker: User
    blog: Blog

    class Config:
        populate_by_name = True
