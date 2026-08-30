from datetime import datetime
from pathlib import Path

from fastapi_mail import MessageSchema
from jinja2 import Environment, FileSystemLoader  # Create HTML from Python data

from app.configs import config
from app.logging.logger import logger
from app.utils.mail import get_mail

# Get file path of HTML
TEMPLATE_DIR = Path(__file__).parent.parent / "templates"
jinja_env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))


# Send welcome email for user
async def send_welcome_email(email: str, name: str) -> None:
    """Render welcome template and send email"""

    # Get HTML template
    template = jinja_env.get_template("welcome_mail.html")

    # Sent data from Python into template literals
    html = template.render(
        name=name,
        server_url=config.SERVER_URL,
        year=datetime.now().year,
    )

    message = MessageSchema(
        subject="Welcome to Book Management 🎉",
        recipients=[email],
        body=html,
        subtype="html",
    )

    try:
        await get_mail().send_message(message)
        logger.info("Welcome email sent to %s", email)
    except Exception as e:
        logger.error("Failed to send email to %s: %s", email, str(e))


# Send OTP email for  (Mobile)
async def send_otp_mail(email: str, name: str, otp_code: str) -> None:
    """Render otp template and send email"""

    # Get HTML template
    template = jinja_env.get_template("otp_mail.html")

    # Sent data from Python into template literals
    html = template.render(
        name=name,
        otp_code=otp_code,
        server_url=config.SERVER_URL,
        year=datetime.now().year,
    )

    message = MessageSchema(
        subject="🔐 Password Reset OTP - Book Management",
        recipients=[email],
        body=html,
        subtype="html",
    )

    try:
        await get_mail().send_message(message)
        logger.info("Reset OTP email sent to %s", email)
    except Exception as e:
        logger.error("Failed to send reset OTP email to %s: %s", email, str(e))


# Send reset password link email (Web)
async def send_reset_link(email: str, name: str, token: str) -> None:
    """Render reset link template and send email"""

    # Get HTML template
    template = jinja_env.get_template("reset_link_mail.html")

    reset_url = f"{config.SERVER_URL}/reset-password?token={token}"
    html = template.render(name=name, reset_url=reset_url)

    message = MessageSchema(
        subject="🔑 Reset Your Password - Book Management",
        recipients=[email],
        body=html,
        subtype="html",
    )

    try:
        await get_mail().send_message(message)
        logger.info("Reset link email sent to %s", email)
    except Exception as e:
        logger.error("Failed to send reset link email to %s: %s", email, str(e))
