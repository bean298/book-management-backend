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
│   ├── routers/                # API routes (auth, user, author, category, book, cart, order, payment)
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
├── pyproject.toml              # Ruff
└── README.md
```

---

## 🧩 Main Features

### 👤 User
- Register & login
- Refresh access token
- View book/categories/authors
- Add book to cart
- Checkout products in cart
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


## 🧹 Code Quality (Ruff)

[Ruff](https://docs.astral.sh/ruff/) is an extremely fast Python **linter + formatter**, written in Rust. It replaces Flake8, isort, pyupgrade, and Black in one tool.


#### `[tool.ruff]` — general settings
| Key | Description |
|-----|-------------|
| `line-length = 90` | Max line width in characters. Exceeding it triggers `E501`. |
| `target-version = "py312"` | Target Python version. Ruff uses it to decide which modern syntax is allowed. |


#### `select` — rule groups to enable:
| Code | Group | What it checks |
|------|-------|----------------|
| `E` | pycodestyle errors | Style/errors: line too long (`E501`), `x == True/False` comparisons (`E712`)… |
| `F` | Pyflakes | Real bugs: unused import (`F401`), unused variable (`F841`), undefined name (`F821`)… |
| `W` | pycodestyle warnings | Whitespace warnings: trailing whitespace (`W291`), blank line issues… |
| `I` | isort | Import sorting & grouping (`I001` unsorted imports)… |
| `UP` | pyupgrade | Modern Python syntax: `Optional[X]` → `X \| None` (`UP045`)… |
| `B` | flake8-bugbear | Bug-prone patterns: mutable default arg (`B006`), bare raise in `except` (`B904`)… |

#### `ignore` — rules to disable:
| Code | Why it is ignored |
|------|-------------------|
| `B008` | FastAPI passes `Depends()` calls as default arguments, which `B008` would false-positive on. |
| `UP046` | Keep `Union[X, Y]` instead of forcing the `X \| Y` syntax. |

#### `[tool.ruff.format]` — formatter settings
| Key | Description |
|-----|-------------|
| `quote-style = "double"` | Use double quotes for strings. |
| `indent-style = "space"` | Indent with spaces, not tabs. |
| `line-ending = "auto"` | Auto-detect line endings (LF / CRLF). |
| `docstring-code-format = true` | Also format code examples inside docstrings. |

### VS Code integration

Install the **Ruff** extension and enable auto-format & import-sort on save in `.vscode/settings.json`:

```json
{
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.fixAll": "explicit",
      "source.organizeImports": "explicit"
    }
  }
}
```

> ⚠️ **SQLAlchemy note:** Ruff's `E712` ("use `not x` instead of `x == False`") does **not** apply to SQLAlchemy columns. In queries, use `.is_(False)` / `.is_(True)` instead of `not`.

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
docker compose up -d --build
```

---

## 🌐 Ngrok (Expose to the Internet)

Add your ngrok authtoken to `.env`:

```env
NGROK_AUTHTOKEN=<your-ngrok-authtoken>
```

Run with Docker (uses the `ngrok` service in `docker-compose.yml`):

```bash
docker compose up -d --build
```

Or run locally (Remember to run app first):

```bash
ngrok http 8000
```

Get the public URL at `http://localhost:4040`, then set it as `SERVER_URL` in `.env` and restart the app so email links (reset password) work:

```env
SERVER_URL=https://<your-subdomain>.ngrok-free.app
```

> ⚠️ On the free plan, the URL changes every restart — update `SERVER_URL` again, or use a fixed domain.

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

