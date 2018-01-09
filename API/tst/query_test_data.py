import pprint
import dynamodb
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

pp = pprint.PrettyPrinter(indent=2)

# response = dynamodb.transactions_table.query(
#     IndexName='TransactionsBySenderNameIndex',
#     KeyConditionExpression=Key('SenderFirstName').eq('John')
# )
#
# pp.pprint(response)
#
# for item in response['Items']:
#     pp.pprint(item)



user_email = 'email1'
try:
    response = dynamodb.logins_table.get_item(
        Key={
            'Email': user_email
        }
    )
except ClientError as e:
    print("hehe")
else:
    if 'Item' not in response or not response['Item']:
        item = {
            "Email": user_email
        }
    else:
        item = response['Item']
    print("Item: {}".format(item))
    if 'Secret' not in item or not item['Secret']:
        item['Secret'] = "secret"
    print("get email successfully: {}".format(item))
