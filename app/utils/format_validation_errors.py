# Format validdation errors for exception validation
def format_validation_errors(
    errors: list[dict],
) -> tuple[str, dict[str, str]]:
    """
    Convert FastAPI validation errors -> (message, field -> message).

    {
        "detail": [
            {
            "type": "value_error",
            "loc": [
                "body",
                "phone"
            ],
            "msg": "Value error, Phone must be a valid Vietnamese mobile number",
            "input": "84902570706",
                "ctx": {
                    "error": {}
                }
            }
        ]
    }

    into

    {
        "detail": "phone: Phone must be a valid Vietnamese mobile number",
        "error_code": "VALIDATION_ERROR",
        "fields": { "phone": "Phone must be a valid Vietnamese mobile number" }
    }
    """
    fields: dict[str, str] = {}

    for err in errors:
        # Get location of the error
        loc = err.get("loc", ())

        field_parts = []

        for part in loc:
            if part != "body" and part != "query" and part != "path":
                field_parts.append(str(part))

        # Convert field location to string
        if len(field_parts) > 0:
            field = ".".join(field_parts)
        else:
            field = "body"

        # Get error message
        msg = err.get("msg", "Invalid input")
        msg = str(msg)

        # Save error to dictionary fields
        if field not in fields:
            fields[field] = msg

    # Check if there are no errors
    if len(fields) == 0:
        return "Invalid input", {}

    # Create general error message
    message_parts = []
    for field, msg in fields.items():
        message_parts.append(f"{field}: {msg}")

    message = "; ".join(message_parts)

    return message, fields
