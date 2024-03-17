import uuid
import datetime
from pydantic import BaseModel as PydanticBaseModel, Field


class BaseModel(PydanticBaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    deleted: bool = False

    class Config:
        populate_by_name = True

