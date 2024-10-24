from typing import Dict
from lecture_2.hw.shop_api.schemas import Item, Cart

current_item_id = 0
current_cart_id = 0


items_db: Dict[int, Item] = {}
carts_db: Dict[int, Cart] = {}