def validate_password(password: str) -> str:
    password = password.strip()

    if len(password) < 6:
        raise ValueError("Password must be at least 6 characters long")
    if len(password.encode("utf-8")) > 72:
        raise ValueError("Password too long")

    return password
