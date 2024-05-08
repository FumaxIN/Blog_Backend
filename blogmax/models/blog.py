import random
import string
from pydantic import Field, constr, BaseModel as PydanticBaseModel
from utils.basemodel import BaseModel

from .user import User


class Blog(PydanticBaseModel):
    title: constr(max_length=100) = Field(...)
    content: constr(max_length=100000) = Field(...)
    tags: list[str] = Field(default_factory=list)

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "title": "My first blog",
                "content": "This is my first blog content",
                "tags": ["tag1", "tag2"],
            }
        }


class BlogUpdate(PydanticBaseModel):
    title: str | None = None
    content: str | None = None
    tags: list[str] | None = Field(default_factory=list)

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "title": "Edited title",
                "content": "Edited content",
                "tags": ["tag1", "tag2"],
            }
        }

class BlogInDB(Blog, BaseModel):
    url: str = Field(default_factory=lambda: "".join(random.choices(string.hexdigits, k=8)))
    reads: int = Field(default=0, read_only=True)
    comments: int = Field(default=0, read_only=True)
    likes: int = Field(default=0, read_only=True)
    author: User

    class Config:
        populate_by_name = True
