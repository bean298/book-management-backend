"""
docs_ui.py: Custom Swagger UI page

Serves a themed (dark, modern) Swagger UI page for the /docs endpoint.
"""

from pathlib import Path

_TEMPLATE_PATH = (
    Path(__file__).resolve().parent.parent / "templates" / "swagger_ui.html"
)


def get_swagger_ui_html() -> str:
    """Return the custom Swagger UI HTML document."""
    return _TEMPLATE_PATH.read_text(encoding="utf-8")
