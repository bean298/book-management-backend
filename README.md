# 📚 Book Management – Backend

Backend API for the Book Management System.

Built with **FastAPI**, **PostgreSQL**, and **RESTful APIs**, supporting authentication, book/category/author management, image upload, and email notification.

This system supports:
- Manage books, authors, categories
- User registration & login with JWT
- Password reset via OTP or email link
- Role access API (Admin & Customer)
- Image upload into MinIO
- Email notification (Welcome, OTP, Reset link)

---

## 🚀 Tech Stack
- Python 3.12
- FastAPI
- SQLAlchemy 2.0
- Pydantic v2
- PostgreSQL 16
- JWT (python-jose)
- bcrypt (password hashing)
- MinIO (S3-compatible image storage)
- Jinja2 + aiosmtplib / fastapi-mail (email)
- Swagger UI
- Uvicorn
- Docker & Docker Compose

---

## 📁 Project Structure

```bash
├── app/                        # Main application
│   ├── main.py                 # FastAPI entry point (app, CORS, lifespan)
│   ├── api/
│   │   └── deps.py             # Auth dependencies (get_current_user, require_admin)
│   ├── configs/
│   │   └── config.py           # Load .env & app configuration
│   ├── constants/
│   │   ├── common.py           # Shared constants
│   │   └── upload.py           # Upload rules (allowed types, max size)
│   ├── core/
│   │   └── s3_minio.py         # MinIO client (upload/delete/presigned URL)
│   ├── db/
│   │   ├── database.py         # Engine, session, Unit of Work
│   │   └── init_db.py          # Create schemas & tables
│   ├── enum/
│   │   └── common.py           # Enums (UserRole, ResetMethod, ...)
│   ├── exceptions/             # Custom exceptions & error codes
│   ├── logging/
│   │   └── logger.py           # Logging configuration
│   ├── models/                 # SQLAlchemy models (ORM)
│   ├── orm/
│   │   ├── postgres.py         # Base model & mixins
│   │   ├── repository.py       # Generic repository
│   │   └── unit_of_work.py     # Unit of Work pattern
│   ├── repositories/           # Data-access per entity
│   ├── routers/                # API routes (auth, user, author, category, book)
│   ├── schemas/                # Pydantic schemas (request/response)
│   ├── services/               # Business logic layer
│   ├── templates/              # Jinja2 templates (email & web)
│   └── utils/                  # Helpers (security, mail, slug, image)
├── logs/                       # Application log files
├── test_data/                  # Seed data (authors, categories, books JSON)
├── docker-compose.yml          # Docker services (db, minio, api)
├── Dockerfile                  # Multi-stage Docker build
├── env.example                 # Environment variables template
├── requirements.txt            # Python dependencies
└── README.md
```

---

## 🧩 Main Features

### 👤 User
- Register & login
- Refresh access token
- View book/categories/authors
- Request password reset via OTP (Mobile) or email link (Web)

### 🧑‍💼 Admin
- Full CRUD users (with pagination & keyword search)
- CRUD books, authors, categories, users

---

## 🗄 Database
- PostgreSQL 16
- Database name: `book_management`
- Schemas: `auth (users, password_reset, refresh_token)` & `book (books, authors, categories)`

---

## 🗂️ Image Storage
- Integrated with MinIO
- Bucket: `book-management-bucket`

---

## ⚙️ Installation & Run

### 1. Clone the repository

```bash
git clone <backend-repo-url>
```

### 2. Create enviroment file

Copy `.env example`

### 3. Run locally (without Docker)

```bash
python -m venv .venv               #Create venv
. venv/Scripts/activate            #Activate venv
pip install -r requirements.txt    #Install denpendencies
python -m app.db.init_db           #Init database
uvicorn app.main:app --reload      #Run app
```

### 4. Run with Docker

```bash
docker compose up --build
```

---

## 🧪 API Documentation

Swagger UI:

```bash
http://localhost:8000/docs
```

ReDoc:

```bash
http://localhost:8000/redoc
```