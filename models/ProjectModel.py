from pydantic import ConfigDict, BaseModel, Field, validator
from bson import ObjectId
from typing import Optional, List
from datetime import datetime
from Enum.ProjectStatusEnum import ProjectStatusEnum


class ProjectRequest(BaseModel):
    client: str
    status: str
    lof_process: str
    date: str
    process: str
    department: str
    billingType: str
    projectLead: str
    rate: float
    comment: Optional[str] = None
    timePerWork: Optional[str] = None
    customfields: List = []


class Project(BaseModel):
    id: Optional[str]
    client: str
    status: ProjectStatusEnum
    lof_process: str
    date: datetime
    process: str
    department: str
    billingType: str
    projectLead: str
    rate: float
    comment: Optional[str] = None
    timePerWork: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
    )

    @validator('date', pre=True)
    def validate_date(cls, value):
        if isinstance(value, str):
            try:
                return datetime.strptime(value, "%m-%d-%Y")
            except ValueError:
                raise ValueError("Date must be in MM-DD-YYYY format")
        return value
