# Checkout Flow — Flow & Logic Notes

> Architecture and processing flow notes for the checkout module of the Book Management project.
> Covers creating an order from the cart (stock validation, order/order-items creation, stock decrement, cart clearing), plus the expired-order rollback job.

---

## 1. Architecture Overview

One-directional pipeline, each layer has one responsibility:

```mermaid
flowchart LR
    FE["Frontend / User"] -->|"POST /order/checkout"| RT["Router<br/>order_router"]
    RT --> SV["Service<br/>order_service.checkout"]
    SV --> RP["Repository<br/>cart / cart_items / order / order_items / books"]
    RP --> DB[("PostgreSQL<br/>via UnitOfWork")]
```

### Core principles

- `order_router` is the **only** HTTP entry point for checkout.
- `order_service.checkout` owns all business validation and database updates; it never touches HTTP details.
- All changes for one checkout run inside a single **UnitOfWork** (auto-commit on success, auto-rollback on error) — creating the order, creating order items, decrementing stock, and clearing the cart are **atomic**.
- Stock is read with a **row lock** (`books.get_by_id_for_update`) to prevent overselling when two users check out the same book concurrently.
- The created order starts as `PENDING` with an `expires_at` deadline — this is the input to the payment flow (`payment_flow.md`).
- The service only works with **cart/order aggregates** — repositories handle the raw SQL/SQLAlchemy queries.

---

## 2. File Map

Ordered top-down, following the request path:

| Layer | File | Role |
|---|---|---|
| Router | `app/routers/order_router.py` | HTTP entry: `POST /order/checkout` |
| Dep | `app/api/deps.py` | `get_current_user` dependency — decodes JWT, returns `User` |
| Service | `app/services/order_service.py` | Business logic: `checkout`, `cancel_expired_orders` |
|  | `app/services/cart_service.py` | `restore_order_items_to_cart` — restore cart after rollback |
| Job | `app/jobs/order_jobs.py` | `run_cancel_expired_orders_job` — scheduled every 30s |
| Repository | `app/repositories/cart_repository.py` | `Cart` queries: `get_by_id` (inherited), `get_cart_by_user_id` |
|  | `app/repositories/cart_item_repository.py` | `CartItem` queries: `get_list_by_cart_id` (eager-loads `book`) |
|  | `app/repositories/order_repository.py` | `Order` queries: `add` (inherited), `get_expired_pending_orders` |
|  | `app/repositories/order_item_repository.py` | `OrderItem` writes: `add` (inherited) |
|  | `app/repositories/book_repository.py` | `Book` queries: `get_by_id_for_update` (row lock + stock) |
|  | `app/repositories/user_repository.py` | `User` queries: `get_by_id` (inherited) |
| Model | `app/models/cart_model.py` | ORM model `Cart` |
|  | `app/models/cart_item_model.py` | ORM model `CartItem` |
|  | `app/models/order_model.py` | ORM model `Order` (+ `order_items` relationship) |
|  | `app/models/order_item_model.py` | ORM model `OrderItem` |
|  | `app/models/book_model.py` | ORM model `Book` |
| Schema | `app/schemas/order_schema.py` | Schemas: `CreateOrderReq`, `OrderRes`, `order_to_res` |
| Enum | `app/enum/common.py` | Enums: `OrderStatus`, `PaymentStatus` |
| DB | `app/orm/unit_of_work.py` | `UnitOfWork` — one DB transaction per HTTP request |
| ORM | `app/orm/repository.py` | Generic `Repository` — `add`, `get_by_id`, `delete` |
| Config | `app/configs/config.py` | `PAYMENT_EXPIRY_MINUTES` — order payment deadline |
