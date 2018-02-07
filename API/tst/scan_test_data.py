import pprint
import aws_client_dynamodb

response = aws_client_dynamodb.transactions_table.scan()

pp = pprint.PrettyPrinter(indent=2)

for item in response['Items']:
    pp.pprint(item)
