# DB / ORM — Flow & Logic Notes

> Architecture and infrastructure notes for the database & ORM layer of the Book Management project.
> Covers connection management, the SQLAlchemy model base, and the generic repository pattern that every feature builds on top of.

---

## 1. Architecture Overview

One-directional dependency chain — each layer depends only on the layer directly below it:

```mermaid
flowchart LR
    CFG["Config<br/>configs/config.py"] -->|"DATABASE_URL, *_SCHEMA, *_TABLE"| DB["DB Context<br/>db/database.py"]
    DB -->|"single PostgresDBContext instance"| ORM["ORM Core<br/>orm/postgres.py"]
    ORM -->|"Base + AppBaseMixin"| MDL["Models<br/>models/*.py"]
    ORM -->|"engine + async_sessionmaker"| DB
    MDL --> REPO["Repositories<br/>repositories/*.py"]
    REPO -->|"inherits Repository[T]"| REPBASE["Base Repository<br/>orm/repository.py"]
    REPBASE -->|"AsyncSession"| DB
```

### Core principles

- `configs/config.py` is the **only** source of DB configuration — it builds `DATABASE_URL` and exposes schema/table names (`AUTH_SCHEMA`, `BOOK_SCHEMA`, `COMMERCE_SCHEMA`, `*_TABLE`).
- `db/database.py` creates **one single `PostgresDBContext` instance** for the whole app (variable `database`); it also defines `IUnitOfWork` and the `get_uow()` factory.
- `orm/postgres.py` contains the low-level ORM pieces:
  - `DBContext` — abstract contract (`session()`, `healthcheck()`, `close()`).
  - `PostgresDBContext` — concrete async engine + connection pooling + `async_sessionmaker`.
  - `Base` (`DeclarativeBase`) — parent of every model; registers all models into SQLAlchemy `metadata`.
  - `AppBaseMixin` — shared columns `created_at`, `updated_at`, `object_status`.
- Every model in `models/*.py` inherits `AppBaseMixin, Base` and declares `__tablename__` + `__table_args__` (schema) from config.
- `orm/repository.py` defines `Repository[T]` — a generic base with `add`, `delete`, `get_by_id`, `paginate` (plus `apply_order_by`). Concrete repos in `repositories/*.py` only add model-specific queries.
- Sessions are **not** created here per query; the `AsyncSession` for one request is opened by `UnitOfWork` (`orm/unit_of_work.py`) — detailed in `unit_of_work.md`.

---

## 2. File Map

Ordered by layer, bottom-up (foundation → application):

| Layer | File | Role |
|---|---|---|
| Config | `app/configs/config.py` | `DATABASE_URL`, `AUTH_SCHEMA`, `BOOK_SCHEMA`, `COMMERCE_SCHEMA`, `*_TABLE`, ... |
| DB | `app/db/database.py` | `database` instance (single PostgresDBContext), `IUnitOfWork`, `get_uow()` factory |
|  | `app/db/init_db.py` | `init_db()` — creates 3 schemas (`auth`, `book`, `commerce`) + `Base.metadata.create_all` |
| ORM | `app/orm/postgres.py` | `DBContext` (abstract), `Base` (DeclarativeBase), `PostgresDBContext`, `AppBaseMixin` |
|  | `app/orm/repository.py` | `Repository[T]` + helper `apply_order_by`, method `paginate` |
| Model | `app/models/*.py` | 11 models inheriting `AppBaseMixin, Base` (list below) |
| Repo | `app/repositories/*.py` | 11 concrete repositories inheriting `Repository[T]` (list below) |

### 11 Models (`app/models/`)

| Model | Table (`__tablename__`) | Schema |
|---|---|---|
| `user_model.py` → `User` | `users` | `auth` |
| `password_reset_model.py` → `PasswordResetToken` | `password_reset` | `auth` |
| `refresh_token_model.py` → `RefreshToken` | `refresh_tokens` | `auth` |
| `author_model.py` → `Author` | `authors` | `book` |
| `book_model.py` → `Book` | `books` | `book` |
| `category_model.py` → `Category` | `categories` | `book` |
| `cart_model.py` → `Cart` | `carts` | `commerce` |
| `cart_item_model.py` → `CartItem` | `cart_items` | `commerce` |
| `order_model.py` → `Order` | `orders` | `commerce` |
| `order_item_model.py` → `OrderItem` | `order_items` | `commerce` |
| `payment_model.py` → `Payment` | `payments` | `commerce` |

> Table/schema names come from `config.py`, not hard-coded in the model.

### 11 Repositories (`app/repositories/`)

| Repository | Inherits | Model |
|---|---|---|
| `user_repository.py` → `UserRepository` | `Repository[User]` | `User` |
| `password_reset_repository.py` → `PasswordResetTokenRepository` | `Repository[PasswordResetToken]` | `PasswordResetToken` |
| `refresh_token_repository.py` → `RefreshTokenRepository` | `Repository[RefreshToken]` | `RefreshToken` |
| `author_repository.py` → `AuthorRepository` | `Repository[Author]` | `Author` |
| `book_repository.py` → `BookRepository` | `Repository[Book]` | `Book` |
| `category_model.py` → `CategoryRepository` | `Repository[Category]` | `Category` |
| `cart_repository.py` → `CartRepository` | `Repository[Cart]` | `Cart` |
| `cart_item_repository.py` → `CartItemRepository` | `Repository[CartItem]` | `CartItem` |
| `order_repository.py` → `OrderRepository` | `Repository[Order]` | `Order` |
| `order_item_repository.py` → `OrderItemRepository` | `Repository[OrderItem]` | `OrderItem` |
| `payment_repository.py` → `PaymentRepository` | `Repository[Payment]` | `Payment` |

---

## 3. How `postgres.py` and `database.py` work

This section explains the "internals" of the two core infrastructure files, with simple examples.

### 3.1 Three concepts to know first

| Concept | Role | Real-world analogy |
|---|---|---|
| **Engine** | Connection pool to Postgres | A telephone exchange — keeps N lines ready |
| **async_sessionmaker** | Session factory | A ticket machine — each press produces a new number (session) |
| **AsyncSession** | Working session: collects SQL then `commit`/`rollback` | A phone call — hang up (close) when done |

Relationship: `engine` → (`sessionmaker`) → `AsyncSession` → `Repository` → SQL.

### 3.2 `orm/postgres.py` — connection management & ORM base

This file defines **4 components**:

1. **`DBContext`** (abstract)
   - Just a "contract" — requires 3 capabilities: `session()`, `healthcheck()`, `close()`.
   - Contains no real code; its purpose is that if you later switch to another DB (MySQL, ...), you only need to write one class that follows this contract.

2. **`Base`** (`DeclarativeBase`)
   - Parent of **every model** (`class Book(AppBaseMixin, Base)`).
   - When a model inherits `Base`, SQLAlchemy automatically:
     - Maps class ↔ table in the DB.
     - Registers the model into `Base.metadata` — so `init_db.py` only needs to call `Base.metadata.create_all` to create **all** tables.

3. **`PostgresDBContext`** — the main class, code in `__init__`:

   ```python
   self.engine = create_async_engine(
       connection_string,        # "postgresql+asyncpg://user:pass@host:port/db"
       pool_size=10,             # connections kept ready
       max_overflow=20,          # allow up to 20 extra connections under load
       pool_pre_ping=True,       # check the connection is alive before use
       pool_recycle=3600,        # recycle connections after 1 hour
   )

   self._sessionmaker = async_sessionmaker(
       self.engine,
       expire_on_commit=False,   # do not "expire" loaded data after commit
   )
   ```

   - `engine` is created **once** (when `database.py` calls `PostgresDBContext(...)`), shared by the whole app.
   - `_sessionmaker` is the "mold" — each call to `session()` casts a new `AsyncSession`.

   The remaining methods are tiny:
   - `session()` → returns a new `AsyncSession` (used for one request).
   - `healthcheck()` → runs `SELECT 1` to check the DB is alive.
   - `close()` → `engine.dispose()` closes the whole pool (called only at app shutdown).

4. **`AppBaseMixin`**
   - Adds 3 shared columns to every table: `created_at`, `updated_at`, `object_status`.
   - Any model inheriting `AppBaseMixin` automatically gets these 3 columns.

### 3.3 `db/database.py` — wiring it all together

This file does **3 things**:

1. **Creates the single instance** (runs once at import):

   ```python
   database = PostgresDBContext(
       connection_string=DATABASE_URL, echo=False, pool_size=10, max_overflow=20
   )
   ```

   - `DATABASE_URL` comes from `config.py`.
   - This `database` variable is **shared across the whole app** — never create a second instance.

2. **`IUnitOfWork`** (Protocol)
   - Just a "declaration" of the attributes `UnitOfWork` must have: `users`, `books`, `payment`, ...
   - Creates no object; its purpose is to let the IDE/type-checker know `uow.books` is a `BookRepository`.

3. **`get_uow()`** — factory, called once per request:

   ```python
   UnitOfWork(
       db=database,
       repositories={"users": UserRepository, "books": BookRepository, ...},
   )
   ```

   - Passes `db=database` (the single instance from step 1).
   - Passes a dict `name → repo class`. `UnitOfWork` uses this dict to create repos lazily (`uow.books` → `BookRepository(session)`), covered in `unit_of_work.md`.

### 3.4 Overall flow at runtime

```mermaid
sequenceDiagram
    participant APP as App (each request)
    participant DB as database.py
    participant PC as PostgresDBContext
    participant S as AsyncSession
    participant R as Repository

    Note over PC: __init__ runs once at import: creates engine + sessionmaker
    APP->>DB: get_uow()
    DB-->>APP: UnitOfWork(db=database, repositories={...})
    APP->>PC: database.session()
    PC->>S: _sessionmaker() → new AsyncSession
    APP->>R: BookRepository(session)
    R->>S: session.execute(SQL)
    S-->>R: result
    R-->>APP: data (Book, list, ...)
    APP->>S: commit() or rollback()
    S->>S: close()
```

One lifecycle in short:

```
import app  →  database (engine + sessionmaker) created once
request     →  get_uow() → UnitOfWork
            →  database.session() → AsyncSession
            →  Repository(session) → execute SQL
            →  commit / rollback → close session
```

---

## 4. Relationship with `unit_of_work.md`

This doc and `unit_of_work.md` complement each other — **no duplicated content**. Clear boundary:

| Topic | Doc |
|---|---|
| `engine`, `async_sessionmaker`, connection pool | `db_orm.md` (section 3.2) |
| `Base`, `AppBaseMixin`, model declaration | `db_orm.md` (sections 1, 2) |
| `Repository[T]`, `apply_order_by`, `paginate` | `db_orm.md` |
| `database` instance + `get_uow()` + `IUnitOfWork` | `db_orm.md` (section 3.3) |
| `UnitOfWork`: `__aenter__`/`__aexit__`, lazy repo creation, auto commit/rollback | `unit_of_work.md` |
| Why 1 request = 1 transaction, when to rollback | `unit_of_work.md` |

In short:

> `db_orm.md` answers **"how to connect to the DB and run one SQL query"**.
> `unit_of_work.md` answers **"how multiple SQL queries in one request form one transaction, when to commit or rollback"**.

Suggested reading order: `db_orm.md` first (engine/session/repo) → `unit_of_work.md` after (how a session is opened/closed around a request).

---

## 5. Example — `GET /book/{book_id}` (file-by-file trace)

A concrete walkthrough: one request that fetches a single book. This is the simplest flow — no auth, no business writes, just one SQL query.

### Request

```http
GET /book/019e4b6e-... HTTP/1.1
```

### Sequence

```mermaid
sequenceDiagram
    participant C as Client
    participant RT as book_router.get_book
    participant DI as deps.get_uow
    participant UOW as UnitOfWork
    participant PC as PostgresDBContext
    participant SV as book_service.get_book
    participant BR as BookRepository
    participant RP as Repository.get_by_id

    C->>RT: GET /book/{book_id}
    RT->>DI: Depends(get_uow)
    DI-->>RT: UnitOfWork(db=database, repositories={...})
    RT->>UOW: async with uow → __aenter__()
    UOW->>PC: database.session()
    PC-->>UOW: new AsyncSession
    RT->>SV: get_book(book_id, uow)
    SV->>UOW: uow.books → __getattr__("books")
    UOW-->>SV: BookRepository(session) (cached)
    SV->>BR: get_by_id(book_id)
    BR->>RP: inherited from Repository
    RP->>PC: session.execute(select(Book) ...)
    PC-->>RP: Book | None
    RP-->>SV: Book
    SV-->>RT: BookRes
    RT->>UOW: __aexit__() → commit() + close()
    RT-->>C: 200 AppBaseResponse
```

### File-by-file trace

1. **`app/routers/book_router.py`** — `get_book`
   - Declares `uow: IUnitOfWork = Depends(get_uow)` and enters `async with uow:`.

2. **`app/db/database.py`** — `get_uow()`
   - FastAPI calls the dependency → returns a brand-new `UnitOfWork(db=database, repositories={...})`.
   - `database` is the **single shared** `PostgresDBContext` (created once at import).

3. **`app/orm/unit_of_work.py`** — `UnitOfWork.__aenter__`
   - `self.session = await self._db.session()` → opens a new `AsyncSession` for this request.

4. **`app/orm/postgres.py`** — `PostgresDBContext.session()`
   - `return self._sessionmaker()` → the sessionmaker casts a new `AsyncSession` from the pool.

5. **`app/services/book_service.py`** — `get_book`
   - Calls `uow.books.get_by_id(book_id)`.

6. **`app/orm/unit_of_work.py`** — `UnitOfWork.__getattr__("books")`
   - `books` is not a real attribute → looks it up in `_repo_factories`, creates `BookRepository(self.session)`, caches it in `_repos`.

7. **`app/repositories/book_repository.py`** — `BookRepository`
   - Does **not** define `get_by_id`; the call falls through to the base class.

8. **`app/orm/repository.py`** — `Repository.get_by_id`
   - Builds `select(Book).where(id == UUID(book_id), object_status == ACTIVE)`.
   - Runs `await self.session.execute(stmt)` → SQL goes to Postgres via the pooled connection.
   - Returns `result.scalar_one_or_none()` (a `Book` or `None`).

9. **`app/services/book_service.py`** — back in `get_book`
   - `None` → raises `NotFoundError`; otherwise converts via `book_to_res(book)` and returns `BookRes`.

10. **`app/routers/book_router.py`** — wraps into `AppBaseResponse` and returns HTTP 200.

11. **`app/orm/unit_of_work.py`** — `UnitOfWork.__aexit__`
    - No exception → `await self.session.commit()`, then `finally: await self.session.close()`.
    - A read-only query doesn't change data, but the transaction is still committed and the session closed uniformly.

### Key takeaways

- The router never touches SQL; it call to `book_service`.
- `book_service` never opens a session; it uses `uow.books` and lets `UnitOfWork` manage the transaction.
- The only file that talks to Postgres is `orm/postgres.py` (via the session from the pool).
