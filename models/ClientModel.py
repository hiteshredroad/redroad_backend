from pydantic import ConfigDict, BaseModel, Field
from bson import ObjectId
from typing import Optional
from datetime import datetime


class Client(BaseModel):
    client: str
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    pinCode: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
    )
