from enum import Enum


class OBJECT_STATUS(str, Enum):
    ACTIVE = 1
    INACTIVE = 0
    DELETE = -1
