from app.schemas.cart_schema import CartRes
from app.db.database import IUnitOfWork
from app.schemas.cart_item_schema import AddToCartReq
from app.schemas.cart_schema import cart_to_res
from app.models.cart_model import Cart
from uuid import UUID
from app.models.cart_item_model import CartItem


# Create cart if not exist, Get cart if existed
async def _get_or_create_cart(
    uow: IUnitOfWork,
    user_id: str | UUID,
) -> Cart:
    cart = await uow.cart.get_cart_by_user_id(str(user_id))
    if cart:
        return cart

    cart = Cart(user_id=UUID(str(user_id)), total_quantity=0, total_price=0)
    return await uow.cart.add(cart)


# Recalculate total quantity, price of cart after add items
async def _recalculate_cart_totals(
    cart: Cart,
    cart_items: list[CartItem],
) -> None:

    # Calculate total price and quantity
    cart.total_quantity = sum(item.quantity for item in cart_items)
    cart.total_price = sum(item.quantity * item.unit_price for item in cart_items)


# Create new cart (when user add product)
async def add_to_cart(
    user_id: str | UUID,
    data: AddToCartReq,
    uow: IUnitOfWork,
) -> CartRes:
    # Check book existing and quantity of book
    book = await uow.books.get_by_id(str(data.book_id))
    if not book:
        raise ValueError(f"Book with ID {data.book_id} does not exist.")
    if book.quantity < 1:
        raise ValueError("This book is out of stock")

    # Get Cart | Create Cart
    cart = await _get_or_create_cart(uow, user_id)

    # Cart Item
    cart_item = await uow.cart_items.get_by_cart_and_book(str(cart.id), str(book.id))

    # Check quantity in cart and in stock
    current_quantity = cart_item.quantity if cart_item else 0
    requested_total_quantity = current_quantity + data.quantity
    if requested_total_quantity > book.quantity:
        raise ValueError(f"Not enough stock. Only {book.quantity} item(s) available.")

    # If product already existed in cart
    if cart_item:
        cart_item.quantity = requested_total_quantity
        cart_item.unit_price = book.price

    # If product havent exist in cart yet
    else:
        item = CartItem(
            cart_id=cart.id,
            book_id=book.id,
            unit_price=book.price,
            quantity=data.quantity,
        )
        await uow.cart_items.add(item)

    # Get all cart items of cart
    cart_items = await uow.cart_items.get_list_by_cart_id(str(cart.id))

    await _recalculate_cart_totals(cart, cart_items)

    return cart_to_res(cart, cart_items, book, user_id)
