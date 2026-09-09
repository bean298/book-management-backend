from enum import StrEnum


class OBJECT_STATUS(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DELETE = "deleted"


class UserRole(StrEnum):
    ADMIN = "admin"
    CUSTOMER = "customer"


class ResetMethod(StrEnum):
    OTP = "otp"
    LINK = "link"


class OrderStatus(StrEnum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class PaymentMethod(StrEnum):
    CASH = "cash"
    CREDIT = "bank_transfer"
    MOMO = "momo"

    @property
    def label(self) -> str:
        return {
            PaymentMethod.CASH: "Cash (COD)",
            PaymentMethod.CREDIT: "Bank Transfer",
            PaymentMethod.MOMO: "Momo",
        }[self]


class PaymentStatus(StrEnum):
    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"
    EXPIRED = "expired"
    REFUNDED = "refunded"
