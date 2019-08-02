import shopify
import datetime
import os
import sys
import iso8601
from functools import partial
from pymongo import MongoClient

def convert_types(order):
    def convert_line_items(item):
        item['price'] = float(item['price'])
        item['pre_tax_price'] = float(item['pre_tax_price'])
        item['total_discount'] = float(item['total_discount'])
        item['tax_lines'] = list(map(convert_tax_lines, item['tax_lines']))

        return item

    def convert_tax_lines(tax_line):
        tax_line['price'] = float(tax_line['price'])
        return tax_line

    # Date fields
    order['created_at'] = iso8601.parse_date(order['created_at'])
    order['updated_at'] = iso8601.parse_date(order['updated_at'])
    order['processed_at'] = iso8601.parse_date(order['processed_at'])

    if order['closed_at'] is not None:
        order['closed_at'] = iso8601.parse_date(order['closed_at'])

    # Price fields
    order['total_price'] = float(order['total_price'])
    order['subtotal_price'] = float(order['subtotal_price'])
    order['total_tax'] = float(order['total_tax'])
    order['total_discounts'] = float(order['total_discounts'])
    order['total_price_usd'] = float(order['total_price_usd'])
    order['total_line_items_price'] = float(order['total_line_items_price'])

    order['line_items'] = list(map(convert_line_items, order['line_items']))
    order['tax_lines'] = list(map(convert_tax_lines, order['tax_lines']))

    return order


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

days_ago = 0 if 'DAYS_AGO' not in os.environ else int(os.environ['DAYS_AGO'])
minutes_ago = 0 if 'MINUTES_AGO' not in os.environ else int(os.environ['MINUTES_AGO'])

if not days_ago and not minutes_ago:
    print("Error: Must specify DAYS_AGO or MINUTES_AGO in environment", file=sys.stderr)
    exit()

tzoffset = datetime.timezone(datetime.timedelta(hours=-7))
start_date = datetime.datetime.now(tz=tzoffset) - datetime.timedelta(days=days_ago,
                                                          minutes=minutes_ago)
print("Fetching orders since", start_date.isoformat())

get_orders_from_start_date = partial(shopify.Order.find,
                                     status="any",
                                     updated_at_min=start_date.isoformat())
orders_res = get_all_orders(get_orders_from_start_date)

process_order = lambda order: convert_types(set_order_id(order))
all_orders = map(process_order,
                    map(lambda order: order.to_dict(), orders_res))

mongo = MongoClient(os.environ['MONGODB_URI'])
upsert_order = partial(mongo.warehouse.shopify_orders.replace_one, upsert=True)

for order in all_orders:
    print(f"Processing order {order['_id']} updated at: {order['updated_at']}") 
    upsert_order({'_id': order['_id']}, order)
