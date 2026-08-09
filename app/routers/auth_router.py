from fastapi import APIRouter, Depends, BackgroundTasks
from app.db.database import get_uow, IUnitOfWork
from app.schemas.user_schema import UserCreateReq, UserRes
from app.schemas.auth_schema import LoginReq, TokenRes
from app.services import auth_service
from app.services.mail_service import send_welcome_email

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserRes)
async def register(
    data: UserCreateReq,
    uow: IUnitOfWork = Depends(get_uow),
    background_tasks: BackgroundTasks = None,
):
    async with uow:
        user = await auth_service.register(uow, data)

    # Sent welcome mail
    background_tasks.add_task(send_welcome_email, email=user.email, name=user.name)
    return user


@router.post("/login", response_model=TokenRes)
async def login(
    data: LoginReq,
    uow: IUnitOfWork = Depends(get_uow),
):
    async with uow:
        res = await auth_service.login(uow, data.email, data.password)
        return res
