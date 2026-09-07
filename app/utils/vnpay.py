import hashlib
import hmac
from datetime import datetime
from urllib.parse import urlencode

from app.configs import config
from app.constants.time import VN_TIMEZONE


# Create HMAC SHA512 signature for VNPAY request parameters
def _secure_hash(params: dict[str, str]) -> str:
    """
    Args:
        params (dict[str, str]): [description]

    Returns:
        str: [description]
    """

    # Create a string of parameters
    # EX:
    #   params = {
    #     vnp_Amount: 100000,
    #     vnp_TxnRef: ORDER001,
    #     vnp_Command: pay
    #   }
    #   sort:
    #     vnp_Amount=100000
    #     vnp_Command=pay
    #     vnp_TxnRef=ORDER001
    #   urlencode:
    #     vnp_Amount=100000&vnp_Command=pay&vnp_TxnRef=ORDER001
    raw = urlencode(sorted(params.items()))

    # Create HMAC SHA512 signature using secret key and raw string
    # EX: 4c3522adaa14c22c63acdb5bd3f3a8ec87ecf812dcdcb70e67d4f5e6594365f8ce5b
    # 98529e7e3c22e32e61baaf8c50cfb25a86b4c73c77f41a0ca801a15c61e3
    return hmac.new(
        config.VNPAY_HASH_SECRET.encode("utf-8"),
        raw.encode("utf-8"),
        hashlib.sha512,
    ).hexdigest()


def build_payment_url(
    *,
    amount: float,
    txn_ref: str,
    order_desc: str,
    ip_address: str,
    expire_at: datetime,
) -> str:
    now = datetime.now(VN_TIMEZONE)

    params = {
        "vnp_Version": "2.1.0",
        "vnp_Command": "pay",
        "vnp_TmnCode": config.VNPAY_TMN_CODE,
        "vnp_Amount": str(int(round(amount * 100))),
        "vnp_CurrCode": "VND",
        "vnp_TxnRef": txn_ref,
        "vnp_OrderInfo": order_desc,
        "vnp_OrderType": "250000",
        "vnp_Locale": "vn",
        "vnp_CreateDate": now.strftime("%Y%m%d%H%M%S"),
        "vnp_ExpireDate": expire_at.astimezone(VN_TIMEZONE).strftime("%Y%m%d%H%M%S"),
        "vnp_IpAddr": ip_address,
        "vnp_ReturnUrl": config.VNPAY_RETURN_URL,
    }

    params["vnp_SecureHash"] = _secure_hash(params)
    return f"{config.VNPAY_URL}?{urlencode(params)}"
