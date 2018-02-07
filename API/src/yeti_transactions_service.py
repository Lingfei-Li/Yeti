import logging
import json
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
import traceback

import yeti_api_response as api_response
from aws_client_dynamodb import transactions_table
from yeti_common_utils import replace_decimals
from yeti_auth_authorizers import LoginAuthorizer
import yeti_constants as constants
import yeti_email_service
import yeti_service_auth
import yeti_exceptions
from yeti_transaction_model_update_history import TransactionUpdateHistory


logger = logging.getLogger("YetiTransactionsService")
logger.setLevel(logging.INFO)


def record_update_history(transaction_id, transaction_platform, action):
    logger.info("Recording action {} for transaction [ {} {} ]".format(action, transaction_id, transaction_platform))
    validate_update_history(transaction_id, transaction_platform)
    # TODO: insert the new action to the update history


def validate_update_history(transaction_id, transaction_platform):
    logger.info("Validating update history for transaction [ {} {} ]".format(transaction_id, transaction_platform))
    update_history = get_update_history(transaction_id, transaction_platform)
    # TODO: validate the update history against the current status


def get_update_history(transaction_id, transaction_platform):
    """
    Get the transaction history

    :param transaction_id:
    :param transaction_platform:
    :return: TransactionUpdateHistory object
    """
    logger.info("Getting update history for transaction [ {} {} ]".format(transaction_id, transaction_platform))
    try:
        response = transactions_table.get_item(
            Key={
                'TransactionId': transaction_id,
                'TransactionPlatform': transaction_platform
            }
        )
    except ClientError as e:
        raise yeti_exceptions.DatabaseAccessErrorException("Failed to read database for TransactionId {} at TransactionPlatform {}. Error: {}".format(transaction_id,
                                                                                                                                                      transaction_platform, e))
    if 'Item' not in response or not response['Item']:
        raise yeti_exceptions.TransactionNotFoundError("TransactionId {} at TransactionPlatform {} doesn't exist".format(transaction_id, transaction_platform))

    transaction = response['Item']

    return TransactionUpdateHistory(json_object=transaction['UpdateHistory'])


