import boto3
import pprint

from test_data import tickets


ticket_table_name = 'Yeti-TicketService-TicketTable'
dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
ticket_table = dynamodb.Table(ticket_table_name)

for ticket in tickets:
    response = ticket_table.put_item(
        Item=ticket
    )

    pp = pprint.PrettyPrinter()
    pp.pprint(ticket)
    print()

print("Put {} records to db".format(len(tickets)))
