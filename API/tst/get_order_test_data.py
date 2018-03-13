import pprint

from aws_client_dynamodb import OrderServiceOrderTable

pp = pprint.PrettyPrinter()

orders = OrderServiceOrderTable.get_orders_for_user_id('lingfeil')

for order in orders:
    pp.pprint(order)
