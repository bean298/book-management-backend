# Payment Flow — Flow & Logic Notes

> Architecture and processing flow notes for the payment module of the Book Management project.
> Covers order payment via VNPay (and Cash/COD), from payment URL creation to callback verification and database updates.

---

## 1. Architecture Overview

One-directional pipeline, each layer has one responsibility:

```mermaid
flowchart LR
    FE["Frontend / User"] -->|"POST /payment"| RT["Router<br/>payment_router"]
    RT --> SV["Service<br/>payment_service"]
    SV --> RP["Repository<br/>payment / order / books"]
    RP --> DB[("PostgreSQL<br/>via UnitOfWork")]
    SV <-->|"build URL / verify callback"| VNP["VNPay Gateway"]
    VNP -->|"GET /payment/vnpay/return"| RT
```

### Layer responsibilities

| Layer | Question | Location |
|---|---|---|
| Router | "Which HTTP request is coming in?" | `app/routers/payment_router.py` |
| Service | "What business rules apply?" | `app/services/payment_service.py` |
| Repository | "How to read/write the database?" | `app/repositories/payment_repository.py`, `app/repositories/order_repository.py` |
| VNPay Utils | "How to sign & verify with the gateway?" | `app/utils/vnpay.py` |
| DB / UnitOfWork | "One request = one transaction" | `app/orm/unit_of_work.py` |

### Core principles

- `payment_router` is the **only** HTTP entry point for payment requests.
- `payment_service` owns all business validation and database updates; it never touches HTTP details.
- The service only works with **order/payment aggregates** — repositories handle the raw SQL/SQLAlchemy queries.
- All database changes for one request run inside a single **UnitOfWork** (auto-commit on success, auto-rollback on error).
- The gateway callback (`/payment/vnpay/return`) is a **separate, unauthenticated** flow — security relies on VNPay's HMAC SHA512 signature, not the user's JWT.

---

## 2. File Map

Ordered top-down, following the request path:

| File | Role |
|---|---|
| `app/main.py` | App wiring; defines `/payment-result` page (renders `payment_result.html`) |
| `app/routers/payment_router.py` | HTTP entry: `POST /payment` and `GET /payment/vnpay/return` |
| `app/api/deps.py` | `get_current_user` dependency — decodes JWT, returns `User` |
| `app/services/payment_service.py` | Business logic: `create_payment`, `process_return`, `_apply_callback_into_db` |
| `app/services/cart_service.py` | `restore_order_items_to_cart` — restore cart after user cancel |
| `app/utils/vnpay.py` | VNPay helpers: `_secure_hash`, `build_payment_url`, `verify_payment`, `parse_vnpay_date` |
| `app/constants/vnpay.py` | `VNP_ERROR_MESSAGES` — map response code → message |
| `app/repositories/payment_repository.py` | `Payment` queries: `get_list_by_order_id`, `get_payment_by_transaction_ref` |
| `app/repositories/order_repository.py` | `Order` queries: `get_order_by_id_with_items` |
| `app/repositories/book_repository.py` | `Book` queries: `get_by_id_for_update` (restock on cancel) |
| `app/repositories/cart_repository.py` | `Cart` queries: `get_cart_by_user_id` |
| `app/repositories/cart_item_repository.py` | `CartItem` queries: `add`, `get_list_by_cart_id` |
| `app/models/payment_model.py` | ORM model `Payment` |
| `app/models/order_model.py` | ORM model `Order` (+ `order_items` relationship) |
| `app/schemas/payment_schema.py` | Schemas: `CreatePaymentReq`, `PaymentRes`, `PaymentUrlRes` |
| `app/enum/common.py` | Enums: `PaymentMethod`, `PaymentStatus`, `OrderStatus` |
| `app/orm/unit_of_work.py` | `UnitOfWork` — one DB transaction per HTTP request |
| `app/db/database.py` | `get_uow()` factory + repository registrations |
| `app/configs/config.py` | VNPay config: `VNPAY_TMN_CODE`, `VNPAY_URL`, `VNPAY_RETURN_URL`, `VNPAY_HASH_SECRET`, `PAYMENT_EXPIRY_MINUTES` |
| `app/templates/payment_result.html` | Success/fail result page rendered by `/payment-result` |

---

## 3. API Endpoints

`app/router/payment_router.py`

| # | Method & Path | Auth | Purpose |
|---|---|---|---|
| 3.1 | `POST /payment` | ✅ Bearer JWT | Create a payment for an order, returns a gateway URL |
| 3.2 | `GET /payment/vnpay/return` | ❌ (signature) | VNPay callback after user pays at the gateway |
| 3.3 | `GET /payment-result` | ❌ | Render the success/fail result page |

### 3.1 `POST /payment` — Create payment

| Aspect | Value |
|---|---|
| Method / Path | `POST /payment` |
| Auth | Required — `Authorization: Bearer <access_token>` (`get_current_user`) |
| Query param | `order_id` (required) |
| Body | `CreatePaymentReq` → `{"method": "cash" \| "bank_transfer" \| "momo"}` |
| Success | `200` — `AppBaseResponse[PaymentUrlRes]` |
| Business error | `Error400` (e.g. order not PENDING, duplicate pending payment) |
| Not found | `404` — `NotFoundError` (order does not exist or not owned) |

**Request**

```http
POST /payment?order_id=019e4b6e-... HTTP/1.1
Authorization: Bearer <access_token>
Content-Type: application/json

{"method": "bank_transfer"}
```

**Response (VNPay method)**

```json
{
  "data": {
    "payment_url": "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html?vnp_Version=2.1.0&vnp_Command=pay&...&vnp_SecureHash=...",
    "payment": {
      "id": "019e4c11-...",
      "order_id": "019e4b6e-...",
      "user_id": "019d5f2a-...",
      "amount": 250000.0,
      "payment_method": "bank_transfer",
      "status": "pending",
      "transaction_ref": "019e4c11-...",
      "gateway_txn_no": null,
      "bank_code": null,
      "pay_date": null,
      "ip_address": "127.0.0.1",
      "error_message": null,
      "created_at": "2026-09-23T07:30:00Z"
    }
  },
  "message": "Payment created successfully"
}
```

> For `method = "cash"`, `payment_url` is `null` (no gateway redirect — paid on delivery).

### 3.2 `GET /payment/vnpay/return` — VNPay callback

| Aspect | Value |
|---|---|
| Method / Path | `GET /payment/vnpay/return` |
| Auth | None — secured by VNPay's HMAC SHA512 signature |
| Query params | Everything VNPay sends back (`vnp_*` + `vnp_SecureHash`) |
| Response | `307` — `RedirectResponse` to `/payment-result?...` |
| In docs | `include_in_schema=False` (hidden from Swagger) |

**Request (from VNPay)**

```http
GET /payment/vnpay/return?vnp_Amount=25000000&vnp_BankCode=NCB&vnp_OrderInfo=Payment+for+order+...&vnp_PayDate=20260923143000&vnp_ResponseCode=00&vnp_TmnCode=...&vnp_TransactionNo=...&vnp_TxnRef=019e4c11-...&vnp_SecureHash=... HTTP/1.1
```

**Response (redirect)**

```http
HTTP/1.1 307 Temporary Redirect
Location: /payment-result?status=success&message=Payment+successful&txn_ref=019e4c11-...&order_id=...&amount=250%2C000&gateway_txn_no=...&method=Bank+Transfer&pay_date=14%3A30+23%2F09%2F2026
```

### 3.3 `GET /payment-result` — Result page

| Aspect | Value |
|---|---|
| Method / Path | `GET /payment-result` |
| Auth | None |
| Query params | `status`, `message`, `txn_ref`, `order_id`, `amount`, `gateway_txn_no`, `method`, `pay_date` |
| Response | `200` — HTML (`payment_result.html`) |

> This route lives in `app/main.py` (not in `payment_router`). It renders the `payment_result.html` template with the query-string values produced by `process_return`.

