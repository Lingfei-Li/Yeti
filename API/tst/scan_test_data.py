import json
import pprint
from src import dynamodb

with open('../../config/cloudformation_config.py') as config_file:
    config = json.load(config_file)

response = dynamodb.transactions_table.scan()

pp = pprint.PrettyPrinter(indent=2)

for item in response['Items']:
    pp.pprint(item)
