from pathlib import Path
from datetime import datetime
from jinja2 import Environment, FileSystemLoader  # Create HTML from Python data
from fastapi_mail import MessageSchema
from app.configs import config
from app.logging.logger import logger
from app.utils.mail import get_mail

# Get file path of HTML
TEMPLATE_DIR = Path(__file__).parent.parent / "templates"
jinja_env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))


# Send email for user
async def send_welcome_email(email: str, name: str) -> None:
    """Render welcome template and send email"""

    # Get HTML template
    template = jinja_env.get_template("welcome.html")

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
