import shopify
import datetime
import os
from functools import partial
from pymongo import MongoClient

def get_all_orders(orders_getter, limit=50):
    """Takes a function that returns orders
    and pages through it until there are no orders left.
    This returns a generator so that orders can be processed as a stream.
    """
    page = 1
    orders = orders_getter(page=page, limit=limit)

    while orders:
        yield from orders
        page += 1
        orders = orders_getter(page=page, limit=limit)

def set_order_id(order):
    order['_id'] = order['id']
    return order

shop_url = "https://{}:{}@{}.myshopify.com/admin".format(os.environ['SHOPIFY_API_KEY'],
                                                         os.environ['SHOPIFY_PASSWORD'],
                                                         os.environ['SHOPIFY_SHOP_NAME'])
shopify.ShopifyResource.set_site(shop_url)

days_ago = 1 if 'DAYS_AGO' not in os.environ else int(os.environ['DAYS_AGO'])
start_date = datetime.datetime.now() - datetime.timedelta(days=days_ago)

get_orders_from_start_date = partial(shopify.Order.find,
                                     status="any",
                                     updated_at_min=start_date.isoformat())
orders_res = get_all_orders(get_orders_from_start_date)

all_orders = map(set_order_id,
                    map(lambda order: order.to_dict(), orders_res))

mongo = MongoClient(os.environ['MONGODB_URI'])
upsert_order = partial(mongo.warehouse.shopify_orders.replace_one, upsert=True)

for order in all_orders:
    upsert_order({'_id': order['_id']}, order)
