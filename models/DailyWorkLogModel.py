from pydantic import ConfigDict, BaseModel, validator
from bson import ObjectId
from typing import Optional, List, Any
from datetime import datetime


class DailyWorkLogExtraField(BaseModel):
    projectExtraFiled: ObjectId
    value: Optional[Any] = None
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
    )

    @validator('projectExtraFiled', pre=True)
    def parse_objectid(cls, v):
        if isinstance(v, str):
            return ObjectId(v)
        return v


class DailyWorkLog(BaseModel):
    projectId: str
    employeeId: str
    employeeName: str
    date: datetime
    workIteams: int
    workHours: str
    customfields: List[DailyWorkLogExtraField] = []
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
