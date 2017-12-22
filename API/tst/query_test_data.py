import json
import pprint
from src import dynamodb
from boto3.dynamodb.conditions import Key

with open('../../config/cloudformation_config.py') as config_file:
    config = json.load(config_file)

pp = pprint.PrettyPrinter(indent=2)

response = dynamodb.transactions_table.query(
    IndexName='TransactionsBySenderNameIndex',
    KeyConditionExpression=Key('SenderFirstName').eq('John')
)

pp.pprint(response)

for item in response['Items']:
    pp.pprint(item)
