import boto3
import pprint

from test_data import tickets


ticket_table_name = 'Yeti-TicketService-TicketTable'
order_ticket_local_view_table_name = 'Yeti-OrderService-TicketLocalView'
dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
ticket_table = dynamodb.Table(ticket_table_name)
order_ticket_local_table = dynamodb.Table(order_ticket_local_view_table_name)
pp = pprint.PrettyPrinter()

for ticket in tickets:
    ticket_table.put_item(
        Item=ticket
    )
    pp.pprint(ticket)
    print()

    order_ticket_local_table.put_item(
        Item=ticket
    )
    pp.pprint(ticket)

    print()


print("Put {} records to db".format(len(tickets)))
