from pydantic import ConfigDict, BaseModel
from bson import ObjectId
from typing import Optional, List, Any
from datetime import datetime


class DailyWorkLogExtraField(BaseModel):
    projectExtraFiled: ObjectId
    value: Optional[Any] = None


class DailyWorkLog(BaseModel):
    projectId: ObjectId
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
