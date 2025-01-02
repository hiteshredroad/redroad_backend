from pydantic import ConfigDict, BaseModel, Field
from bson import ObjectId
from datetime import datetime


class LofBuisness(BaseModel):
    lofBuisness: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
    )
