from fastapi import Response

from app.configs import config


# Set cookies into HttpOnly cookie
def set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    """Set access/refresh token into HttpOnly cookie."""
    common = {
        "httponly": True,
        # Defines whether the cookie should only be sent over HTTPS.
        "secure": config.COOKIE_SECURE,
        # Control browser sent cookie through request
        "samesite": config.COOKIE_SAMESITE,
        "domain": config.COOKIE_DOMAIN or None,
    }

    response.set_cookie(
        key=config.ACCESS_COOKIE_NAME,
        value=access_token,
        max_age=config.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
        **common,
    )
    response.set_cookie(
        key=config.REFRESH_COOKIE_NAME,
        value=refresh_token,
        max_age=config.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
        path=config.REFRESH_COOKIE_PATH,
        **common,
    )


# Clear Cookies when logout
def clear_auth_cookies(response: Response) -> None:
    """Clear Cookies when logout."""
    response.delete_cookie(config.ACCESS_COOKIE_NAME, path="/")
    response.delete_cookie(config.REFRESH_COOKIE_NAME, path=config.REFRESH_COOKIE_PATH)
