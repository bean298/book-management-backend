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