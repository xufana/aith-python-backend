import http
from fastapi import APIRouter, Query, Response, HTTPException
from lecture_2.hw.shop_api.schemas.cart import Cart, CartItem
from lecture_2.hw.shop_api.dbs import carts_db, items_db, current_cart_id
from typing import Optional, List


router = APIRouter(prefix='/cart', tags=['Работа с корзиной'])

@router.post("/", status_code=http.HTTPStatus.CREATED, response_model=Cart)
async def create_cart(response: Response) -> Cart:
    global current_cart_id
    current_cart_id += 1
    carts_db[current_cart_id] = Cart(id=current_cart_id, items=[])
    response.headers["location"] = f"/cart/{current_cart_id}"
    return carts_db[current_cart_id]


@router.get("/{id}", status_code=http.HTTPStatus.OK, response_model=Cart)
async def get_cart_by_id(id: int) -> Cart:
    cart = carts_db.get(id)
    if cart is None:
        raise HTTPException(status_code=http.HTTPStatus.NOT_FOUND, detail="Cart not found")
    item_list, total_price, _ = get_cart_info(id)
    return Cart(id=id, items=item_list, price=total_price)

@router.post("/{cart_id}/add/{item_id}")
async def add_item(cart_id: int, item_id: int) -> Cart:
    item = items_db.get(item_id)
    if item is None or item.deleted: 
        raise HTTPException(status_code=http.HTTPStatus.NOT_FOUND, detail="Item not found")
    cart = carts_db.get(cart_id)
    if cart is None: 
        raise HTTPException(status_code=http.HTTPStatus.NOT_FOUND, detail="Cart not found")

    item_ids = [cart_item.id for cart_item in cart.items]
    if item_id not in item_ids:
        cart.items.append(CartItem(id=item_id, name=item.name, quantity=1, avaliable=not item.deleted))
    elif item_id in item_ids:
        cart.items[item_ids.index(item_id)].quantity += 1
    
    item_list, total_price, _ = get_cart_info(cart_id)
    return Cart(id=cart_id, items=item_list, price=total_price)

def get_cart_info(cart_id: int) -> list[int, float, int]:
    item_list = []
    total_price = 0
    quantity = 0
    cart = carts_db.get(cart_id)
    for item in cart.items:
        item_list.append(item)
        total_price += items_db[item.id].price * item.quantity
        quantity += item.quantity

    return item_list, total_price, quantity

@router.get("/")
async def get_cart_by_filter(offset: int = Query(0, ge=0),
                    limit: int = Query(10, gt=0),
                    min_price: Optional[float] = Query(None, gt=0),
                    max_price: Optional[float] = Query(None, gt=0),
                    min_quantity: Optional[int] = Query(None, gt=0),
                    max_quantity: Optional[int] = Query(None, ge=0),
                    ) -> list[Cart]:

    filtered_carts: List[Cart] = list(filter(lambda cart: (
            (min_price is None or get_cart_info(cart.id)[1] >= min_price) and
            (max_price is None or get_cart_info(cart.id)[1] <= max_price) and
            (min_quantity is None or get_cart_info(cart.id)[2] >= min_quantity) and
            (max_quantity is None or get_cart_info(cart.id)[2] <= max_quantity)
    ), carts_db.values()))
    filtered_carts = filtered_carts[offset:offset + limit]

    processed_carts = []
    for cart in filtered_carts:
        items, price, _ = get_cart_info(cart.id)
        processed_carts.append(Cart(id=cart.id, items=items, price=price))
    return processed_carts