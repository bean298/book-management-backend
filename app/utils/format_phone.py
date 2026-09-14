# Validate Vietnamese mobile phone number
def validate_vn_phone(phone: int | None) -> int | None:
    if phone is None:
        return phone

    s = str(phone)
    # 11 numbers, and start with 84 (+84)
    valid = len(s) == 11 and s.startswith("84") and s[2] in "35789"
    if not valid:
        raise ValueError(
            "Phone must be a valid Vietnamese mobile number (e.g. 0912345678)"
        )
    return phone
