from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.configs import config
from contextlib import asynccontextmanager
import uvicorn
from app.logging.logger import logger
from app.exceptions.base_exception import BaseAppException
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from app.routers.auth_router import router as auth_router
from app.routers.user_router import router as user_router
from app.routers.author_router import router as author_router
from app.routers.category_router import router as category_router
from app.routers.book_router import router as book_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("App startup")
    yield
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
    swagger_ui_parameters={
        "syntaxHighlight": True,  # Highlight syntax in Swagger UI
        "tryItOutEnabled": True,  # Turn on "Try it out" button in Swagger UI
        "displayRequestDuration": True,  # Display request duration in Swagger UI
        "filter": True,
    },
    lifespan=lifespan,  # Lifespan event
    redirect_slashes=False,
)

# Jinja2 templates for serving web pages
templates = Jinja2Templates(directory="app/templates")


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow domain (dev)
    allow_credentials=True,
    allow_methods=["*"],  # Allow methods (GET, POST...)
    allow_headers=["*"],  # Allow headers (Authorization...)
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


# When user click in button in reset link mail, redirect user to URL {config.SERVER_URL}/reset-password?token={token}
# This router will match the URL, and render html file (reset_password.html) for user to enter new password and attach token
@app.get("/reset-password", include_in_schema=False)
async def reset_password_page(request: Request, token: str = ""):
    """Render the web page for resetting password."""
    return templates.TemplateResponse(request, "reset_password.html", {"token": token})


# Include Routers
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(author_router)
app.include_router(category_router)
app.include_router(book_router)


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=config.PORT, reload=True)
