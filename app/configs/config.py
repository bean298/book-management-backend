import os
from urllib.parse import quote

from dotenv import load_dotenv

load_dotenv()

ENV = os.getenv("BOOK_MANAGEMENT_ENV", default="DEV")
PORT = int(os.getenv("BOOK_MANAGEMENT_PORT", default="8000"))
SERVER_URL = os.getenv("SERVER_URL", default="http://localhost:8000")

# DB (defaults for local development)
DB_NAME = os.getenv("BOOK_MANAGEMENT_DB_NAME", default="book_management")
DB_USER = os.getenv("BOOK_MANAGEMENT_DB_USER", default="postgres")
DB_PASSWORD = quote(os.getenv("BOOK_MANAGEMENT_DB_PASSWORD", default="123123"))
DB_HOST = os.getenv("BOOK_MANAGEMENT_DB_HOST", default="localhost")
DB_PORT = int(os.getenv("BOOK_MANAGEMENT_DB_PORT", default="5432"))

DATABASE_URL = (
    f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# JWT
# ⚠️ Override JWT_SECRET_KEY in production
JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", default="dev-secret-change-me")
JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", default="HS256")
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", default="30")
)
REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
REFRESH_TOKEN_LENGTH: int = 64

# SCHEMA
AUTH_SCHEMA = os.getenv("BOOK_MANAGEMENT_AUTH_SCHEMA", default="auth")
BOOK_SCHEMA = os.getenv("BOOK_MANAGEMENT_BOOK_SCHEMA", default="book")
COMMERCE_SCHEMA = os.getenv("BOOK_MANAGEMENT_COMMERCE_SCHEMA", default="commerce")

# TABLE
USER_TABLE = os.getenv("BOOK_MANAGEMENT_USER_TABLE", default="users")
AUTHOR_TABLE = os.getenv("BOOK_MANAGEMENT_AUTHOR_TABLE", default="authors")
BOOK_TABLE = os.getenv("BOOK_MANAGEMENT_BOOK_TABLE", default="books")
CATEGORY_TABLE = os.getenv("BOOK_MANAGEMENT_CATEGORY_TABLE", default="categories")
PASSWORD_RESET_TABLE = os.getenv(
    "BOOK_MANAGEMENT_PASSWORD_RESET_TABLE", default="password_reset"
)
REFRESH_TOKEN_TABLE = os.getenv("BOOK_MANAGEMENT_REFRESH_TOKEN_TABLE", "refresh_tokens")
CART_ITEMS_TABLE = os.getenv("BOOK_MANAGEMENT_CART_ITEMS_TABLE", default="cart_items")
CART_TABLE = os.getenv("BOOK_MANAGEMENT_CART_TABLE", default="carts")
ORDER_TABLE = os.getenv("BOOK_MANAGEMENT_ORDER_TABLE", default="orders")
ORDER_ITEMS_TABLE = os.getenv("BOOK_MANAGEMENT_ORDER_ITEMS_TABLE", default="order_items")
PAYMENT_TABLE = os.getenv("BOOK_MANAGEMENT_PAYMENT_TABLE", default="payments")

# MAIL
MAIL_USERNAME: str = os.getenv("MAIL_USERNAME", default="")
MAIL_PASSWORD: str = os.getenv("MAIL_PASSWORD", default="")
MAIL_FROM: str = os.getenv("MAIL_FROM", default="")
MAIL_PORT: int = int(os.getenv("MAIL_PORT", "587"))
MAIL_SERVER: str = os.getenv("MAIL_SERVER", "smtp.gmail.com")
MAIL_STARTTLS: bool = os.getenv("MAIL_TLS", "True") == "True"
MAIL_SSL_TLS: bool = os.getenv("MAIL_SSL", "False") == "True"

# MinIO
MINIO_HOST = os.getenv("BOOK_MANAGEMENT_MINIO_HOST", default="localhost:9000")
MINIO_ACCESS_KEY = os.getenv("BOOK_MANAGEMENT_MINIO_ACCESS_KEY", default="")
MINIO_SECRET_KEY = os.getenv("BOOK_MANAGEMENT_MINIO_SECRET_KEY", default="")
MINIO_REGION = os.getenv("BOOK_MANAGEMENT_MINIO_REGION", default="us-east-1")
MINIO_BUCKET = os.getenv(
    "BOOK_MANAGEMENT_MINIO_PI_BUCKET", default="book-management-bucket"
)

# VNPay
VNPAY_TMN_CODE: str = os.getenv("VNPAY_TMN_CODE", default="")
VNPAY_HASH_SECRET: str = os.getenv("VNPAY_HASH_SECRET", default="")
VNPAY_URL: str = os.getenv(
    "VNPAY_URL", default="https://sandbox.vnpayment.vn/paymentv2/vpcpay.html"
)
VNPAY_RETURN_URL: str = os.getenv(
    "VNPAY_RETURN_URL", default=f"{SERVER_URL}/payment/vnpay/return"
)
VNPAY_IPN_URL: str = os.getenv("VNPAY_IPN_URL", default=f"{SERVER_URL}/payment/vnpay/ipn")
PAYMENT_EXPIRY_MINUTES: int = int(os.getenv("PAYMENT_EXPIRY_MINUTES", "10"))
