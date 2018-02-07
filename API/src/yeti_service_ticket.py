import datetime
import logging
import json
import traceback

import aws_client_dynamodb
import uuid
import yeti_api_response

import yeti_exceptions
import yeti_models
import yeti_service_order
import yeti_utils_lambda_handler
from aws_client_kinesis import PaymentServiceMessageNotificationStream

logger = logging.getLogger("YetiTicketService")
logger.setLevel(logging.INFO)


def get_ticket(ticket_id):
    # TODO: get the ticket info from ddb
    # return yeti_models.Ticket()
    pass

