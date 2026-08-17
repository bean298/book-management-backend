from app.schemas.cart_schema import CartRes
from app.db.database import IUnitOfWork
from app.schemas.cart_item_schema import AddToCartReq
from app.schemas.cart_schema import cart_to_res
from app.models.cart_model import Cart
from uuid import UUID
from app.models.cart_item_model import CartItem
from app.exceptions.resource_exception import NotFoundError
from app.logging.logger import logger


# Create new cart (when user add product)
async def add_to_cart(
    user_id: str | UUID,
    data: AddToCartReq,
    uow: IUnitOfWork,
) -> CartRes:
    """
    Args:
        user_id (str): [description]
        data (AddToCartReq): [description]
        uow (IUnitOfWork): [description]

    Raises:
        ValueError: [description]
        ValueError: [description]
        ValueError: [description]

    Returns:
        CartRes: [description]
    """
    # Check book existing and quantity of book
    book = await uow.books.get_by_id(str(data.book_id))
    if not book:
        logger.warning("Add to cart failed: book not found | book_id=%s", data.book_id)
        raise ValueError(f"Book with ID {data.book_id} does not exist.")
    if book.quantity < 1:
        logger.warning("Add to cart failed: book out of stock | book_id=%s", book.id)
        raise ValueError("This book is out of stock")

    # Get Cart | Create Cart
    cart = await _get_or_create_cart(uow, user_id)

    # Cart Item
    cart_item = await uow.cart_items.get_by_cart_and_book(str(cart.id), str(book.id))

    # Check quantity in cart and in stock
    current_quantity = cart_item.quantity if cart_item else 0
    requested_total_quantity = current_quantity + data.quantity
    if requested_total_quantity > book.quantity:
        logger.warning(
            "Add to cart failed: not enough stock | book_id=%s, requested=%s, available=%s",
            book.id,
            requested_total_quantity,
            book.quantity,
        )
        raise ValueError(f"Not enough stock. Only {book.quantity} item(s) available.")

    # If product already existed in cart
    if cart_item:
        cart_item.quantity = requested_total_quantity
        cart_item.unit_price = book.price
        logger.info(
            "Cart item updated | cart_id=%s, book_id=%s, quantity=%s",
            cart.id,
            book.id,
            cart_item.quantity,
        )

    # If product havent exist in cart yet
    else:
        item = CartItem(
            cart_id=cart.id,
            book_id=book.id,
            unit_price=book.price,
            quantity=data.quantity,
        )
        await uow.cart_items.add(item)
        logger.info(
            "Cart item created | cart_id=%s, book_id=%s, quantity=%s",
            cart.id,
            book.id,
            data.quantity,
        )

    # Get all cart items of cart
    cart_items = await uow.cart_items.get_list_by_cart_id(str(cart.id))

    await _recalculate_cart_totals(cart, cart_items)

    logger.info(
        "Cart updated | cart_id=%s, user_id=%s, total_quantity=%s, total_price=%s",
        cart.id,
        user_id,
        cart.total_quantity,
        cart.total_price,
    )

    return cart_to_res(cart, cart_items, str(user_id))


# Get cart of user (current user)
async def get_cart_of_user(user_id: str, uow: IUnitOfWork) -> CartRes:
    """
    Args:
        user_id (str): [description]
        uow (IUnitOfWork): [description]

    Raises:
        NotFoundError: [description]

    Returns:
        CartRes: [description]
    """
    cart = await uow.cart.get_cart_by_user_id(str(user_id))
    if not cart:
        logger.warning("Get cart failed: cart not found | user_id=%s", user_id)
        raise NotFoundError()

    cart_items = await uow.cart_items.get_list_by_cart_id(str(cart.id))

    logger.info("Get cart of user | cart_id=%s, user_id=%s", cart.id, user_id)
    return cart_to_res(cart, cart_items, str(cart.user_id))


# Get cart (Admin)
async def get_cart(cart_id: str, uow: IUnitOfWork) -> CartRes:
    """
    Args:
        cart_id (str): [description]
        uow (IUnitOfWork): [description]

    Raises:
        NotFoundError: [description]

    Returns:
        CartRes: [description]
    """
    cart = await uow.cart.get_by_id(str(cart_id))
    if not cart:
        logger.warning("Get cart (admin) failed: cart not found | cart_id=%s", cart_id)
        raise NotFoundError()

    cart_items = await uow.cart_items.get_list_by_cart_id(str(cart.id))

    logger.info("Get cart (admin) | cart_id=%s", cart.id)
    return cart_to_res(cart, cart_items, str(cart.user_id))


# Delete cart item
async def delete_cart_item(cart_item_id: str, user_id: str, uow: IUnitOfWork) -> None:
    # Get cart of user
    cart = await uow.cart.get_cart_by_user_id(str(user_id))
    if not cart:
        logger.warning("Cant found cart of this user")
        raise NotFoundError()

    # Get cart item
    item = await uow.cart_items.get_by_id(str(cart_item_id))
    if not item:
        logger.warning(
            "Delete cart item failed: item not found | cart_item_id=%s", cart_item_id
        )
        raise NotFoundError()

    # Make sure item belong to user's cart
    if item.cart_id != cart.id:
        logger.warning(
            "Delete cart item failed: item does not belong to cart "
            "| cart_item_id=%s, cart_id=%s",
            cart_item_id,
            cart.id,
        )
        raise NotFoundError()

    await uow.cart_items.delete(item)

    # Get all cart items of cart
    cart_items = await uow.cart_items.get_list_by_cart_id(str(cart.id))

    await _recalculate_cart_totals(cart, cart_items)

    logger.info(
        "Cart item deleted | cart_id=%s, cart_item_id=%s, "
        "total_quantity=%s, total_price=%s",
        cart.id,
        cart_item_id,
        cart.total_quantity,
        cart.total_price,
    )


# Create cart if not exist, Get cart if existed
async def _get_or_create_cart(
    uow: IUnitOfWork,
    user_id: str | UUID,
) -> Cart:
    cart = await uow.cart.get_cart_by_user_id(str(user_id))
    if cart:
        return cart

    cart = Cart(user_id=UUID(str(user_id)), total_quantity=0, total_price=0)
    new_cart = await uow.cart.add(cart)

    logger.info("Cart created | cart_id=%s, user_id=%s", new_cart.id, user_id)
    return new_cart


# Recalculate total quantity, price of cart after add items
async def _recalculate_cart_totals(
    cart: Cart,
    cart_items: list[CartItem],
) -> None:

    # Calculate total price and quantity
    cart.total_quantity = sum(item.quantity for item in cart_items)
    cart.total_price = sum(item.quantity * item.unit_price for item in cart_items)
