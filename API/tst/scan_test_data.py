import pprint
import yeti_dynamodb

response = yeti_dynamodb.transactions_table.scan()

pp = pprint.PrettyPrinter(indent=2)

for item in response['Items']:
    pp.pprint(item)
