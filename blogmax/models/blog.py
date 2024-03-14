import random
import string
from pydantic import Field, constr
from essentials.basemodel import BaseModel


class Blog(BaseModel):
    title: constr(max_length=100) = Field(...)
    content: constr(max_length=100000) = Field(...)
    url: str = Field(default_factory=lambda: "".join(random.choices(string.hexdigits, k=8)))
    reads: int = Field(default=0)
    comments: int = Field(default=0)
    likes: int = Field(default=0)

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "title": "My first blog",
                "content": "This is my first blog content",
            }
        }

