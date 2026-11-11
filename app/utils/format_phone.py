# Validate Vietnamese mobile phone number
def validate_vn_phone(phone: str | None) -> str | None:
    if phone is None:
        return phone

    s = str(phone)

    # 12 numbers, and start with 84 (+84)
    # or 9 number
    valid = (len(s) == 9 and s[0] in "35789") or (
        len(s) == 12 and s.startswith("+84") and s[3] in "35789" and s[3:].isdigit()
    )
    if not valid:
        raise ValueError(
            "Phone must be a valid Vietnamese mobile number (e.g. 0912345678)"
        )
    return phone
