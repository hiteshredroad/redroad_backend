from pydantic import ConfigDict, BaseModel
from bson import ObjectId
from Enum.FieldDataTypeEnum import FieldDataTypeEnum


class ProjectExtraField(BaseModel):
    projectId: str
    label: str
    dataType: FieldDataTypeEnum
    fieldName: str
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
    )
