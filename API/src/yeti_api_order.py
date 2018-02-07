import logging
import json
import traceback

import yeti_api_response
import aws_client_dynamodb
import yeti_exceptions
import yeti_models
import yeti_service_order
import yeti_utils_lambda_handler

logger = logging.getLogger("YetiOrderApi")
logger.setLevel(logging.INFO)


def handle_payment_notification(event, context):
    try:
        logger.info("Received a payment notification: {}".format(event))
        message = json.loads(event['Records'][0]['Sns']['Message'])

        payment = yeti_models.Payment.from_sns_message(message)

        aws_client_dynamodb.OrderServicePaymentLocalView.put_payment_item(payment)

        logger.info("Payment inserted to local view")
    except yeti_exceptions.YetiApiBadEventBodyException as e:
        logger.info("The request body doesn't match payment notification message schema. Error: {}".format(e))


def handle_ticket_notification(event, context):
    try:
        logger.info("Received a ticket notification: {}".format(event))
        message = json.loads(event['Records'][0]['Sns']['Message'])

        ticket = yeti_models.Ticket.from_sns_message(message)

        aws_client_dynamodb.OrderServiceTicketLocalView.put_ticket_item(ticket)

        logger.info("Ticket inserted to local view")
    except yeti_exceptions.YetiApiBadEventBodyException as e:
        logger.info("The request body doesn't match ticket notification message schema. Error: {}".format(e))


def create_order(event, context):
    # TODO: testing
    logger.info("Received a create order request: {}".format(event))

    try:
        # TODO: Auth

        body = yeti_utils_lambda_handler.get_body(event)

        ticket_id = body['ticket_id']
        purchase_amount = body['purchase_amount']
        buyer_id = body['buyer_id']

        logger.info("Received an order: ticket id: {}, buying amount: {}, buyer_id: {}".format(ticket_id, purchase_amount, buyer_id))

        yeti_service_order.create_order(ticket_id, purchase_amount, buyer_id)

        return yeti_api_response.ok_no_data()

    except yeti_exceptions.YetiApiClientErrorException as e:
        return yeti_api_response.client_error(str(e))

    except (yeti_exceptions.YetiApiInternalErrorException, Exception) as e:
        logger.error(traceback.format_exc())
        return yeti_api_response.internal_error(str(e))

