import json
import traceback

import yeti_api_response
import aws_client_dynamodb
import yeti_exceptions
import yeti_logging
import yeti_models
import yeti_service_order
import yeti_utils_lambda_handler

logger = yeti_logging.get_logger("YetiOrderApi")


def handle_payment_notification(event, context):
    try:
        logger.info("Received a payment notification: {}".format(event))
        message = json.loads(event['Records'][0]['Sns']['Message'])
        notification_type = message['notification_type']
        serialized_data = message['serialized_data']
        order_id = message['order_id']
        data = json.loads(serialized_data)

        yeti_service_order.handle_payment_notification(notification_type, data, order_id)

    except yeti_exceptions.YetiApiBadEventBodyException as e:
        logger.info("The request body doesn't match payment notification message schema. Error: {}".format(e))
    except (yeti_exceptions.YetiApiClientErrorException, yeti_exceptions.DatabaseItemNotFoundError) as e:
        logger.info("Client-side problems occurred when processing payment notification: {}".format(e))
    except (yeti_exceptions.YetiApiInternalErrorException, Exception)as e:
        logger.error(traceback.format_exc())
        logger.error("Encountered internal problems processing payment notification: {}".format(e))


def handle_ticket_notification(event, context):
    try:
        logger.info("Received a ticket notification: {}".format(event))
        message = json.loads(event['Records'][0]['Sns']['Message'])

        ticket = yeti_models.Ticket.from_sns_message(message)

        aws_client_dynamodb.OrderServiceTicketLocalView.put_ticket_item(ticket)

        logger.info("Ticket inserted to local view")
    except yeti_exceptions.YetiApiBadEventBodyException as e:
        logger.info("The request body doesn't match ticket notification message schema. Error: {}".format(e))


def get_all_orders_for_user(event, context):
    logger.info("Received a create order request: {}".format(event))

    try:
        # TODO: Auth
        headers = yeti_utils_lambda_handler.get_headers(event)
        user_email = headers['user_email']

        orders = yeti_service_order.get_orders_for_user_email(user_email)

        return yeti_api_response.ok(orders)

    except (yeti_exceptions.YetiApiClientErrorException, yeti_exceptions.DatabaseItemNotFoundError) as e:
        return yeti_api_response.client_error(str(e))

    except (yeti_exceptions.YetiApiInternalErrorException, Exception) as e:
        logger.error(traceback.format_exc())
        return yeti_api_response.internal_error(str(e))


def create_order(event, context):
    logger.info("Received a create order request: {}".format(event))

    try:
        # TODO: Auth

        body = yeti_utils_lambda_handler.get_body(event)

        # Other attributes (order id, order version, order datetime, expiry) will be inserted by the backend service.
        ticket_list = body['ticket_list']
        buyer_email = body['buyer_email']

        logger.info("Received an order: ticket list: {}, buyer_email: {}".format(ticket_list, buyer_email))

        order_id = yeti_service_order.create_order(ticket_list, buyer_email)

        return yeti_api_response.ok({'order_id': order_id})

    except (yeti_exceptions.YetiApiClientErrorException, yeti_exceptions.DatabaseItemNotFoundError) as e:
        return yeti_api_response.client_error(str(e))

    except (yeti_exceptions.YetiApiInternalErrorException, Exception) as e:
        logger.error(traceback.format_exc())
        return yeti_api_response.internal_error(str(e))

