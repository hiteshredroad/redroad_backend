from pydantic import ConfigDict, BaseModel, Field, EmailStr, root_validator
from bson import ObjectId
from typing import Optional, List, Dict, Any
from typing_extensions import Annotated
from pydantic.functional_validators import BeforeValidator
from datetime import datetime
from Enum import ProjectStatusEnum 

class DailyWorkLogExtraField(BaseModel):
    projectExtraFiled:ObjectId
    value:Optional[Any] = None

class DailyWorkLog(BaseModel):
    projectId: ObjectId
    employeeId:str
    employeeName:str
    date:datetime
    workIteams:int
    workHours:str
    extraFields : List[DailyWorkLogExtraField] = []
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
    )