import os
from dotenv import load_dotenv
from urllib.parse import quote

load_dotenv()

ENV = os.getenv("BOOK_MANAGEMENT_ENV", default="DEV")
PORT = int(os.getenv("BOOK_MANAGEMENT_PORT", default="8000"))
SERVER_URL = os.getenv("SERVER_URL", default="http://localhost:8000")

# DB
DB_NAME = os.getenv("BOOK_MANAGEMENT_DB_NAME")
DB_USER = os.getenv("BOOK_MANAGEMENT_DB_USER")
DB_PASSWORD = quote(os.getenv("BOOK_MANAGEMENT_DB_PASSWORD"))
DB_HOST = os.getenv("BOOK_MANAGEMENT_DB_HOST")
DB_PORT = int(os.getenv("BOOK_MANAGEMENT_DB_PORT"))

DATABASE_URL = (
    f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# SCHEMA
AUTH_SCHEMA = os.getenv("BOOK_MANAGEMENT_AUTH_SCHEMA", default="auth")
BOOK_SCHEMA = os.getenv("BOOK_MANAGEMENT_BOOK_SCHEMA", default="book")

# TABLE
USER_TABLE = os.getenv("BOOK_MANAGEMENT_USER_TABLE")
AUTHOR_TABLE = os.getenv("BOOK_MANAGEMENT_AUTHOR_TABLE")
BOOK_TABLE = os.getenv("BOOK_MANAGEMENT_BOOK_TABLE")
CATEGORY_TABLE = os.getenv("BOOK_MANAGEMENT_CATEGORY_TABLE")
PASSWORD_RESET_TABLE = os.getenv("BOOK_MANAGEMENT_PASSWORD_RESET_TABLE")

# MAIL
MAIL_USERNAME: str = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD: str = os.getenv("MAIL_PASSWORD")
MAIL_FROM: str = os.getenv("MAIL_FROM")
MAIL_PORT: int = int(os.getenv("MAIL_PORT", "587"))
MAIL_SERVER: str = os.getenv("MAIL_SERVER", "smtp.gmail.com")
MAIL_STARTTLS: bool = os.getenv("MAIL_TLS", "True") == "True"
MAIL_SSL_TLS: bool = os.getenv("MAIL_SSL", "False") == "True"
