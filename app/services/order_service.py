from app.db.database import IUnitOfWork
from app.exceptions.resource_exception import NotFoundError
from app.logging.logger import logger
from app.schemas.order_schema import OrderRes, CreateOrderReq
from app.models.order_model import Order
from app.models.order_item_model import OrderItem
from app.schemas.order_schema import order_to_res
from app.enum.common import OrderStatus


# Checkout
async def checkout(
    user_id: str, cart_id: str, data: CreateOrderReq, uow: IUnitOfWork
) -> OrderRes:
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
