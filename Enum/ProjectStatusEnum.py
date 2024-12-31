
from enum import Enum


class ProjectStatusEnum(str, Enum):
    ACTIVE = 'active'
    IN_ACTIVE = 'in_active'
    ON_HOLD = 'on_hold'
