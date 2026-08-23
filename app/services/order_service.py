from app.db.database import IUnitOfWork
from app.exceptions.resource_exception import NotFoundError
from app.logging.logger import logger
from app.schemas.order_schema import OrderRes, CreateOrderReq
from app.models.order_model import Order
from app.models.order_item_model import OrderItem
from app.schemas.order_schema import order_to_res
from app.enum.common import OrderStatus
from app.schemas.base_schema import AppBasePagingRes
from app.enum.common import OrderStatus
from typing import Optional


# Checkout
async def checkout(
    user_id: str, cart_id: str, data: CreateOrderReq, uow: IUnitOfWork
) -> OrderRes:
    """
    Args:
        user_id (str): [description]
        cart_id (str): [description]
        data (CreateOrderReq): [description]
        uow (IUnitOfWork): [description]

    Raises:
        ValueError: [description]
        NotFoundError: [description]

    Returns:
        OrderRes: [description]
    """
    # Get cart
    cart = await uow.cart.get_by_id(str(cart_id))
    if not cart:
        raise ValueError("Can't find cart")

    # Ensure take right cart of user
    if str(cart.user_id) != str(user_id):
        raise NotFoundError("Cart", cart_id)

    # Get cart item
    cart_items = await uow.cart_items.get_list_by_cart_id(str(cart.id))
    if not cart_items:
        raise ValueError("Cart is empty")

    # Get user
    user = await uow.users.get_by_id(str(user_id))
    if not user:
        raise NotFoundError()

    # Get book and check book
    for item in sorted(cart_items, key=lambda item: str(item.book_id)):
        book = await uow.books.get_by_id_for_update(str(item.book_id))
        if not book:
            raise NotFoundError("Book", str(item.book_id))
        if item.quantity <= 0:
            raise ValueError("Cart contains an invalid quantity")
        if item.quantity > book.quantity:
            logger.warning(
                "Checkout failed: insufficient stock | book_id=%s, requested=%s, available=%s",
                book.id,
                item.quantity,
                book.quantity,
            )
            raise ValueError(f"Not enough stock for '{book.title}'")

        item.book = book

    # Create new order
    order = await uow.order.add(
        Order(
            user_id=user.id,
            total_quantity=sum(item.quantity for item in cart_items),
            total_price=sum(item.quantity * item.unit_price for item in cart_items),
            status=OrderStatus.PENDING,
            payment_method=data.payment_method,
            shipping_address=data.shipping_address,
        )
    )

    # Create order items
    created_order_items: list[OrderItem] = []
    for cart_item in cart_items:
        order_item = await uow.order_items.add(
            OrderItem(
                order_id=order.id,
                book_id=cart_item.book_id,
                book_name=cart_item.book.title,
                unit_price=cart_item.unit_price,
                quantity=cart_item.quantity,
            )
        )

        # Load information of book
        order_item.book = cart_item.book
        created_order_items.append(order_item)

        # Decrement stock
        cart_item.book.quantity -= cart_item.quantity

    # Delete cart items
    for item in cart_items:
        await uow.cart_items.delete(item)

    # Update cart
    cart.total_price = 0
    cart.total_quantity = 0

    logger.info(
        "Checkout succeeded | order_id=%s, user_id=%s, cart_id=%s",
        order.id,
        user.id,
        cart.id,
    )

    return order_to_res(order, created_order_items, user)


# Get all orders of a user
async def list_orders(
    user_id: str,
    uow: IUnitOfWork,
    page: int = 1,
    page_size: int = 10,
    status: Optional[OrderStatus] = None,
) -> AppBasePagingRes[OrderRes]:
    """
    Args:
        user_id (str): [description]
        uow (IUnitOfWork): [description]
        page (int, optional): [description]. Defaults to 1.
        page_size (int, optional): [description]. Defaults to 10.

    Returns:
        AppBasePagingRes[OrderRes]: [description]
    """
    data = await uow.order.get_list_paginate_orders_by_user_id(
        user_id, page=page, page_size=page_size, status=status
    )

    return AppBasePagingRes[OrderRes](
        items=[
            order_to_res(order, order.order_items, order.user)
            for order in data["items"]
        ],
        total=data["total"],
        page=data["page"],
        page_size=data["page_size"],
        is_full=data["is_full"],
    )


# Get order of a user
async def get_order(
    order_id: str,
    user_id: str,
    uow: IUnitOfWork,
) -> OrderRes:
    """
    Args:
        order_id (str): [description]
        user_id (str): [description]
        uow (IUnitOfWork): [description]

    Raises:
        NotFoundError: [description]

    Returns:
        OrderRes: [description]
    """
    order = await uow.order.get_order_by_id_with_items(order_id)
    if not order:
        raise NotFoundError("Order", order_id)

    if str(order.user_id) != str(user_id):
        raise NotFoundError("Order", order_id)

    return order_to_res(order, order.order_items, order.user)


# Get all order (ADMIN)
async def list_orders_admin(
    user_id: str,
    uow: IUnitOfWork,
    page: int = 1,
    page_size: int = 10,
    status: Optional[OrderStatus] = None,
) -> AppBasePagingRes[OrderRes]:
    data = await uow.order.get_list_paginate_orders_by_user_id(
        user_id, page=page, page_size=page_size, status=status
    )
