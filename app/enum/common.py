from enum import Enum


class OBJECT_STATUS(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DELETE = "deleted"


class UserRole(str, Enum):
    ADMIN = "admin"
    CUSTOMER = "customer"


class ResetMethod(str, Enum):
    OTP = "otp"
    LINK = "link"
