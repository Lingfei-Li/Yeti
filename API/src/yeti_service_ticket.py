import aws_client_dynamodb
import yeti_logging

logger = yeti_logging.get_logger("YetiTicketService")


def get_ticket(ticket_id, ticket_version):
    # TODO: get the ticket info from ddb
    # return yeti_models.Ticket()
    pass


def get_all_tickets():
    return aws_client_dynamodb.TicketServiceTicketTable.get_all_tickets()
