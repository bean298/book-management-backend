from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.configs import config
from app.core.docs_ui import get_swagger_ui_html
from app.exceptions.base_exception import BaseAppException
from app.jobs.order_jobs import shutdown_order_scheduler, start_order_scheduler
from app.logging.logger import logger
from app.routers.auth_router import router as auth_router
from app.routers.author_router import router as author_router
from app.routers.book_router import router as book_router
from app.routers.cart_router import router as cart_router
from app.routers.category_router import router as category_router
from app.routers.order_router import router as order_router
from app.routers.payment_router import router as payment_router
from app.routers.user_router import router as user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("App startup")

    start_order_scheduler()

    yield

    shutdown_order_scheduler()

    logger.info("App shutdown")


# FastAPI app
app = FastAPI(
    title="Book Management App",
    description="Simple API to manage books, authors, categories, and book covers",
    version="1.0.0",
    terms_of_service="https://fastapi.tiangolo.com/tutorial/metadata/",
    contact={
        "name": "API Support",
        "url": "https://www.facebook.com/tuan.nguyen.374077/?locale=vi_VN",
        "email": "tuannase171419@fpt.edu.vn",
    },
    license_info={"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
    docs_url=None,  # Disable the default Swagger UI
    lifespan=lifespan,  # Lifespan event
    redirect_slashes=False,
)

# Jinja2 templates for serving web pages
templates = Jinja2Templates(directory="app/templates")


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all domain (dev)
    allow_credentials=False,
    allow_methods=[
        "GET",
        "POST",
        "PUT",
        "DELETE",
        "OPTIONS",
    ],  # Allow methods
    allow_headers=["Authorization", "Content-Type"],  # Allow headers
)


# Exception Handler
@app.exception_handler(BaseAppException)
async def app_exception_handler(request: Request, exc: BaseAppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "error_code": exc.error_code,
        },
    )


@app.get("/health")
async def health():
    return {"status": "ok"}


# Custom themed Swagger UI (dark, modern)
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui():
    return HTMLResponse(get_swagger_ui_html())


# When user click in button in reset link mail, redirect user to URL
# ## {config.SERVER_URL}/reset-password?token={token}
# This router will match the URL, and render html file (reset_password.html) for user to
# ## enter new password and attach token
@app.get("/reset-password", include_in_schema=False)
async def reset_password_page(request: Request, token: str = ""):
    """Render the web page for resetting password."""
    return templates.TemplateResponse(request, "reset_password.html", {"token": token})


# Simulate case return to front-end
@app.get("/payment-result", include_in_schema=False)
async def payment_result(
    request: Request,
    status: str = "failed",
    message: str = "",
    txn_ref: str = "",
    order_id: str = "",
    amount: str = "",
    gateway_txn_no: str = "",
    method: str = "",
    pay_date: str = "",
):
    """Render success/fail page"""
    return templates.TemplateResponse(
        request,
        "payment_result.html",
        {
            "status": status,
            "message": message,
            "txn_ref": txn_ref,
            "order_id": order_id,
            "amount": amount,
            "gateway_txn_no": gateway_txn_no,
            "method": method,
            "pay_date": pay_date,
        },
    )


API_PREFIX = "/api/v1"

# Include Routers
app.include_router(auth_router, prefix=API_PREFIX)
app.include_router(user_router, prefix=API_PREFIX)
app.include_router(author_router, prefix=API_PREFIX)
app.include_router(category_router, prefix=API_PREFIX)
app.include_router(book_router, prefix=API_PREFIX)
app.include_router(cart_router, prefix=API_PREFIX)
app.include_router(order_router, prefix=API_PREFIX)
app.include_router(payment_router, prefix=API_PREFIX)


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=config.PORT, reload=True)
