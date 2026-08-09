from fastapi_mail import FastMail, ConnectionConfig
from app.configs import config

_mail: FastMail | None = None


# Init Object FastMail only the first time send mail
def get_mail() -> FastMail:
    """Lazy init FastMail — avoid crash when env vars missing"""

    global _mail
    if _mail is None:
        mail_config = ConnectionConfig(
            MAIL_USERNAME=config.MAIL_USERNAME,
            MAIL_PASSWORD=config.MAIL_PASSWORD,
            MAIL_FROM=config.MAIL_FROM,
            MAIL_PORT=config.MAIL_PORT,
            MAIL_SERVER=config.MAIL_SERVER,
            MAIL_STARTTLS=config.MAIL_STARTTLS,
            MAIL_SSL_TLS=config.MAIL_SSL_TLS,
            USE_CREDENTIALS=True,
        )
        _mail = FastMail(mail_config)
    return _mail
