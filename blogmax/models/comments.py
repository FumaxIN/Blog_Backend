from pydantic import Field, constr, BaseModel as PydanticBaseModel
from utils.basemodel import BaseModel

from .user import User
from .blog import BlogInDB


class Comment(BaseModel):
    content: constr(max_length=1000) = Field(...)

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "content": "Type your comment",
            }
        }


class CommentInDB(Comment, BaseModel):
    blog: BlogInDB = Field(...)
    commenter: User = Field(...)

    class Config:
        populate_by_name = True
