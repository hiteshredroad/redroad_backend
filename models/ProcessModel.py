from pydantic import ConfigDict, BaseModel, Field, EmailStr, root_validator
from bson import ObjectId
from typing import Optional, List
from typing_extensions import Annotated
from pydantic.functional_validators import BeforeValidator
from datetime import datetime


class Process(BaseModel):
    process: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
    )