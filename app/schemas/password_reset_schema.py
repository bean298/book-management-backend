from typing import Annotated, Literal

from pydantic import AfterValidator, BaseModel, EmailStr, Field

from app.utils.format_password import validate_password

# Annotated password
NewPassword = Annotated[
    str,
    Field(None, description="NewPassword"),
    AfterValidator(validate_password),  # Validate password
]


class ForgetPasswordReq(BaseModel):
    """Schema for step 1: Request sent OTP or link"""

    email: EmailStr = Field(..., description="Email of user")
    method: Literal["otp", "link"] = Field(
        default="link", description="otp = mobile | link = web"
    )


class ResetPasswordReq(BaseModel):
    """Schema confirm and change pass (Both Web and Mobile)"""

    reset_token: str = Field(..., description="Token from OTP or Link email")
    new_password: NewPassword


class MessageResponse(BaseModel):
    message: str


# ---- SCHEMA FOR MOBILE ----
class VerifyOTPReq(BaseModel):
    """Schema for Verify OTP (Mobile Only)"""

    email: EmailStr = Field(..., description="Email of user")
    otp_code: str = Field(..., min_length=6, description="OTP code")


class VerifyOTPRes(BaseModel):
    """Schema response after verify OTP success (Mobile Only)"""

    reset_token: str = Field(..., description="Temporary token to change password")
    message: str
