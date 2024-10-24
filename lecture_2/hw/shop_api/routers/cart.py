import http
from fastapi import APIRouter, Query, Response, HTTPException
from lecture_2.hw.shop_api.schemas import Cart, CartItem, ItemPut, ItemUpd
from lecture_2.hw.shop_api.dbs import carts_db, items_db, current_cart_id
from typing import Optional, List


router = APIRouter(prefix='/cart', tags=['Работа с корзиной'])

@router.post("/", status_code=http.HTTPStatus.CREATED)
async def create_cart(response: Response) -> Cart:
    global current_cart_id
    current_cart_id += 1
    carts_db[current_cart_id] = Cart(id=current_cart_id, items=[])
    response.headers["Location"] = f"/cart/{current_cart_id}"
    return carts_db[current_cart_id]

@router.get("/{id}")
async def get_cart_by_id(id: int) -> Cart:
    cart = carts_db.get(id)
    if cart is None or cart.avaliable: 
        raise HTTPException(status_code=http.HTTPStatus.NOT_FOUND, detail="Cart not found")
    return cart

@router.post("/{cart_id}/add/{item_id}")
async def add_item(cart_id: int, item_id: int) -> Cart:
    item = items_db.get(item_id)
    if item is None or item.deleted: 
        raise HTTPException(status_code=http.HTTPStatus.NOT_FOUND, detail="Item not found")
    cart = carts_db.get(id)
    if cart is None or cart.avaliable: 
        raise HTTPException(status_code=http.HTTPStatus.NOT_FOUND, detail="Cart not found")
    items = cart.items
    for i, cart_item in enumerate(items):
        if cart_item.id == item_id:
            items[i].quantity += 1
            break
    else:
        items.append(item)
    price = cart.price + item.price
    carts_db[cart_id] = Cart(id = cart_id, items=items, price=price)
    return carts_db[cart_id]

@router.get("/")
async def get_cart_by_filter(offset: int = Query(0, ge=0),
                    limit: int = Query(10, gt=0),
                    min_price: Optional[float] = Query(None, gt=0),
                    max_price: Optional[float] = Query(None, gt=0),
                    min_quantity: Optional[int] = Query(None, gt=0),
                    max_quantity: Optional[int] = Query(None, gt=0),
                    ) -> list[Cart]:
    filtered_carts: List[Cart] = list(filter(lambda cart: (
            (min_price is None or cart.price >= min_price) and
            (max_price is None or cart.price <= max_price) and
            (min_quantity is None or cart.price >= min_price) and
            (max_quantity is None or cart.price <= max_price)
    ), carts_db.values()))
    filtered_carts = filtered_carts[offset:offset + limit]
    return filtered_carts