import yeti_dynamodb

response = yeti_dynamodb.transactions_table.scan()

for item in response['Items']:
    response = yeti_dynamodb.transactions_table.delete_item(
        Key={
            "TransactionId": item['TransactionId'],
            "TransactionPlatform": item['TransactionPlatform']
        }
    )
    print(response)



