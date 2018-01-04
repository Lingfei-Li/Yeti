import dynamodb

response = dynamodb.transactions_table.scan()

for item in response['Items']:
    response = dynamodb.transactions_table.delete_item(
        Key={
            "TransactionId": item['TransactionId']
        }
    )
    print(response)



