from pydantic import ConfigDict, BaseModel, Field, EmailStr, validator
from bson import ObjectId
from typing import Optional, List, Dict, Any
from typing_extensions import Annotated
from pydantic.functional_validators import BeforeValidator
from datetime import datetime
from Enum.ProjectStatusEnum import ProjectStatusEnum 

class ProjectRequest(BaseModel):
    client : str
    status : str
    lof_process : str
    date : str
    process:str
    department:str
    billingType : str
    projectLead : str
    rate : float
    comment:Optional[str] = None
    timePerWork : Optional[str] = None
    customfields : List = []

class Project(BaseModel):
    id: Optional[str]
    client : str
    status : ProjectStatusEnum
    lof_process : str
    date : datetime
    process:str
    department:str
    billingType : str
    projectLead : str
    rate : float
    comment:Optional[str] = None
    timePerWork : Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
    )
    @validator('date', pre=True)
    def validate_date(cls, value):
        # If the date is in MM-DD-YYYY format, convert it to YYYY-MM-DD
        if isinstance(value, str):
            try:
                # Try to parse using MM-DD-YYYY format
                return datetime.strptime(value, "%m-%d-%Y")
            except ValueError:
                # If it doesn't match, let Pydantic handle it as an invalid format
                raise ValueError("Date must be in MM-DD-YYYY format")
        return value