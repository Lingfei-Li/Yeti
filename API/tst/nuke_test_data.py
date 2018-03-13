import aws_client_dynamodb

response = aws_client_dynamodb.transactions_table.scan()

for item in response['Items']:
    response = aws_client_dynamodb.transactions_table.delete_item(
        Key={
            "TransactionId": item['TransactionId'],
            "TransactionPlatform": item['TransactionPlatform']
        }
    )
    print(response)



