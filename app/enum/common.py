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


class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class PaymentMethod(str, Enum):
    CASH = "cash"
    CREDIT = "bank_transfer"
    MOMO = "momo"
