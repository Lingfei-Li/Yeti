import pprint
from src import dynamodb

response = dynamodb.transactions_table.scan()

pp = pprint.PrettyPrinter(indent=2)

for item in response['Items']:
    pp.pprint(item)
