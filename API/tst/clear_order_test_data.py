import boto3

dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
table_name = 'Yeti-OrderService-OrderTable'
table = dynamodb.Table(table_name)

response = table.scan()

total_orders = len(response['Items'])

for item in response['Items']:
    response = table.delete_item(
        Key={
            "order_id": item['order_id'],
            "order_version": item['order_version'],
        }
    )
    print(response)

print("Delete {} records from db".format(total_orders))

