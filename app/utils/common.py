from fastapi.responses import JSONResponse

from app.schemas.base_schema import AppBaseResponse


def Error400(msg: str):
    return JSONResponse(
        status_code=400,
        content=AppBaseResponse(
            message=msg,
            status_code=400,
        ).model_dump(),
    )
