import traceback

import aws_client_sns
import yeti_api_response
import aws_client_dynamodb
import yeti_exceptions
import yeti_logging
import yeti_models
import yeti_service_ticket
import yeti_utils_lambda_handler

logger = yeti_logging.get_logger("YetiTicketApi")


# Lambda handler for create ticket, update ticket, etc
def create_ticket(event, context):
    logger.info("Received a create ticket request: {}".format(event))

    try:
        # TODO: Auth

        body = yeti_utils_lambda_handler.get_body(event)

        ticket = yeti_models.Ticket.build(
            ticket_amount=body['ticket_amount'],
            ticket_type=body['ticket_type'],
            distributor_email=body['distributor_email'],
            distribution_location=body['distribution_location'],
            distribution_start_datetime=body['distribution_start_datetime'],
            distribution_end_datetime=body['distribution_end_datetime'],
        )

        logger.info("Ticket to create: {}".format(ticket.to_json()))

        # Check duplication
        if aws_client_dynamodb.TicketServiceTicketTable.is_exist(ticket):
            logger.info("Ticket with the same attributes already exists")
            return yeti_api_response.ok('Ticket with the same details already exists. Insertion considered successful for idempotency.')

        # Insert ticket to db
        aws_client_dynamodb.TicketServiceTicketTable.put_ticket_item(ticket)
        logger.info("Ticket inserted to DB")

        # Notify other services about the ticket via SNS
        ticket_notification_message = ticket
        aws_client_sns.TicketServiceTicketNotificationTopic.publish_message(ticket_notification_message)
        logger.info("Ticket notification published to SNS")

        return yeti_api_response.ok_no_data()

    except yeti_exceptions.YetiApiClientErrorException as e:
        return yeti_api_response.client_error(str(e))

    except (yeti_exceptions.YetiApiInternalErrorException, Exception) as e:
        logger.error(traceback.format_exc())
        return yeti_api_response.internal_error(str(e))


# Lambda handler for get all tickets
def get_all_tickets(event, context):
    logger.info("Received a get all tickets request: {}".format(event))
    try:
        # TODO: Auth

        tickets = yeti_service_ticket.get_all_tickets()

        return yeti_api_response.ok(tickets)

    except yeti_exceptions.YetiApiClientErrorException as e:
        return yeti_api_response.client_error(str(e))

    except (yeti_exceptions.YetiApiInternalErrorException, Exception) as e:
        logger.error(traceback.format_exc())
        return yeti_api_response.internal_error(str(e))

