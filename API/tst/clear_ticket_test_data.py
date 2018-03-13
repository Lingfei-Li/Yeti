import boto3

ticket_table_name = 'Yeti-TicketService-TicketTable'
order_ticket_local_view_table_name = 'Yeti-OrderService-TicketLocalView'
dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
ticket_table = dynamodb.Table(ticket_table_name)
order_ticket_local_table = dynamodb.Table(order_ticket_local_view_table_name)

response = ticket_table.scan()

for item in response['Items']:
    response = ticket_table.delete_item(
        Key={
            "ticket_id": item['ticket_id'],
            "ticket_version": item['ticket_version'],
        }
    )
    print(response)


response = order_ticket_local_table.scan()
for item in response['Items']:
    response = order_ticket_local_table.delete_item(
        Key={
            "ticket_id": item['ticket_id'],
            "ticket_version": item['ticket_version'],
        }
    )
    print(response)
