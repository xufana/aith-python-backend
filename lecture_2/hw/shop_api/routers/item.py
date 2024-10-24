import http
from fastapi import APIRouter, Query, HTTPException
from lecture_2.hw.shop_api.schemas.item import Item, ItemCreate, ItemPut, ItemUpd
from lecture_2.hw.shop_api.dbs import items_db, current_item_id
from typing import Optional, List


router = APIRouter(prefix='/item', tags=['Работа с товарами'])

@router.post("/", status_code=http.HTTPStatus.CREATED, response_model=Item)
async def add_item(item: ItemCreate) -> Item:
    global current_item_id
    current_item_id += 1
    items_db[current_item_id] = Item(id=current_item_id, name=item.name, price=item.price)
    print(items_db[current_item_id])
    return items_db[current_item_id]

@router.get("/{id}")
async def get_item_by_id(id: int) -> Item:
    item = items_db.get(id)
    if item is None or item.deleted: 
        raise HTTPException(status_code=http.HTTPStatus.NOT_FOUND, detail="Item not found")
    return item

@router.put("/{id}")
async def replace_item(id: int, item: ItemPut) -> Item:
    if id not in items_db:
        raise HTTPException(status_code=http.HTTPStatus.NOT_FOUND, detail="Item not found")
    items_db[id] = Item(id=id, name=item.name, price=item.price, deleted=item.deleted)
    return items_db[id]

@router.patch("/{id}")
async def alter_item(id: int, new_item: Optional[ItemUpd] = None) -> Item:
    current_item = items_db.get(id)
    if current_item and not current_item.deleted:
        if new_item is None:
            return items_db[id]
        name = new_item.name if new_item.name is not None else current_item.name
        price = new_item.price if new_item.price is not None else current_item.price
        items_db[id] = Item(id=id, name=name, price=price, deleted=current_item.deleted)
        return items_db[id]
    else:
        raise HTTPException(status_code=http.HTTPStatus.NOT_MODIFIED, detail="Error occured")

@router.delete("/{id}")
async def delete_item(id: int) -> Item:
    item = items_db.get(id)
    if item is None: 
        raise HTTPException(status_code=http.HTTPStatus.NOT_FOUND, detail="Item not found")
    else:
        items_db[id] = Item(id=id, name=item.name, price=item.price, deleted=True)
    return items_db[id]

@router.get("/")
async def get_item_by_filter(offset: int = Query(0, ge=0),
                    limit: int = Query(10, gt=0),
                    min_price: Optional[float] = Query(None, gt=0),
                    max_price: Optional[float] = Query(None, gt=0),
                    show_deleted: Optional[bool] = False
                    ) -> list[Item]:
    filtered_items: List[Item] = list(filter(lambda item: (
            (min_price is None or item.price >= min_price) and
            (max_price is None or item.price <= max_price) and
            (show_deleted or not item.deleted)
    ), items_db.values()))
    filtered_items = filtered_items[offset:offset + limit]
    return filtered_items