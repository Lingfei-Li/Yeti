import json
import decimal
import boto3
from cloudformation_config import config


# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)


# Initialize DynamoDB connections
dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
transactions_table = dynamodb.Table(config['YetiTransactionsTableName'])
logins_table = dynamodb.Table(config['YetiLoginsTableName'])
devices_table = dynamodb.Table(config['YetiDevicesTableName'])
