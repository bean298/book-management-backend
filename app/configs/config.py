import os
from dotenv import load_dotenv
from urllib.parse import quote

load_dotenv()

ENV = os.getenv("BOOK_MANAGEMENT_ENV", default="DEV")
PORT = int(os.getenv("BOOK_MANAGEMENT_PORT", default="8000"))

# DB
DB_NAME = os.getenv("BOOK_MANAGEMENT_DB_NAME")
DB_USER = os.getenv("BOOK_MANAGEMENT_DB_USER")
DB_PASSWORD = quote(os.getenv("BOOK_MANAGEMENT_DB_PASSWORD"))
DB_HOST = os.getenv("BOOK_MANAGEMENT_DB_HOST")
DB_PORT = int(os.getenv("BOOK_MANAGEMENT_DB_PORT"))
