from pydantic import ConfigDict, BaseModel, Field, EmailStr, root_validator
from bson import ObjectId
from typing import Optional, List
from typing_extensions import Annotated
from pydantic.functional_validators import BeforeValidator
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
    


class ClientCollection(BaseModel):
    data: List[Client]
