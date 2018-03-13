import boto3
import pprint
from test_data import orders

dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
table_name = 'Yeti-OrderService-OrderTable'
table = dynamodb.Table(table_name)
pp = pprint.PrettyPrinter()

for item in orders:
    table.put_item(
        Item=item
    )
    pp.pprint(item)

    print()


print("Put {} records to db".format(len(orders)))
