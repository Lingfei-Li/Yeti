import json
from src import dynamodb

with open('./test_data.py') as test_data_file:
    test_data = json.load(test_data_file)

for item in test_data:
    response = dynamodb.transactions_table.delete_item(
        Key={
            "TransactionId": item['TransactionId']
        }
    )
    print(response)





