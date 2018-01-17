import logging
import json
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

import api_response as api_response
from dynamodb import transactions_table
from utils import replace_decimals
from auth import LoginAuthorizer
import constants as constants

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def transform_emails(event, context):
    logger.info("Got a transform email request: {}".format(event))
    error_response, login_email = LoginAuthorizer.auth_non_login_event(event)
    if error_response is not None:
        return error_response

    # Transform logic for login_email

    return api_response.ok_no_data("success")


