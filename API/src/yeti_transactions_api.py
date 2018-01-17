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


def load_transactions(event, context):
    print(event)
    error_response, login_email = LoginAuthorizer.auth_non_login_event(event)
    if error_response is not None:
        return error_response

    # Only return transactions sent to the login email
    filter_expression = Key('UserEmail').eq(login_email)

    response = transactions_table.scan(
        ProjectionExpression="UserId, FriendId, FriendName, Amount, TransactionUnixTimestamp, StatusCode, TransactionId, TransactionPlatform, Comments",
        FilterExpression=filter_expression
    )

    data = []
    for item in response['Items']:
        item = replace_decimals(item)
        data.append(item)

    return api_response.ok({
        'count': response['Count'],
        'data': data
    })


def close_transaction(event, context):
    error_response, login_email = LoginAuthorizer.auth_non_login_event(event)
    if error_response is not None:
        return error_response

    # Get transaction id from path parameter
    try:
        body = json.loads(event['body'])
    except (KeyError, TypeError, ValueError):  # By default Lambda sets the body to None if it's left empty -> TypeError
        logger.info("Cannot parse request body to JSON object. ")
        return api_response.client_error("Cannot parse request body to JSON object. ")
    try:
        transaction_id = body['transactionId']
        transaction_platform = body['transactionPlatform']
        logger.info('closing transaction id: {}, platform: {}'.format(transaction_id, transaction_platform))
    except KeyError:
        return api_response.client_error("Cannot read property 'transactionId' or 'transactionPlatform' from path parameters. ")

    # Check if the transaction id exists
    try:
        response = transactions_table.get_item(
            Key={
                'TransactionId': transaction_id,
                'TransactionPlatform': transaction_platform
            }
        )
    except ClientError as e:
        logger.info(e.response['Error']['Message'])
        return api_response.internal_error(e.response['Error']['Message'])
    if 'Item' not in response or not response['Item']:
        return api_response.not_found("TransactionId {} at TransactionPlatform {} doesn't exist".format(transaction_id, transaction_platform))

    # Update the StatusCode of the transaction.
    # Currently, it doesn't check for current StatusCode. Simply overrides the status to completed
    transactions_table.update_item(
        Key={
            'TransactionId': transaction_id,
            'TransactionPlatform': transaction_platform
        },
        UpdateExpression="set StatusCode = :s",
        ExpressionAttributeValues={
            ':s': constants.TransactionStatusCode.completed
        }
    )

    logger.info("Transaction [ id: {}, platform: {} ] closed successfully".format(transaction_id, transaction_platform))
    return api_response.ok_no_data("Transaction [ id: {}, platform: {} ] closed successfully".format(transaction_id, transaction_platform))


def reopen_transaction(event, context):
    error_response, login_email = LoginAuthorizer.auth_non_login_event(event)
    if error_response is not None:
        return error_response

    # Get transaction id from path parameter
    try:
        body = json.loads(event['body'])
    except (KeyError, TypeError, ValueError):  # By default Lambda sets the body to None if it's left empty -> TypeError
        logger.info("Cannot parse request body to JSON object. ")
        return api_response.client_error("Cannot parse request body to JSON object. ")
    try:
        transaction_id = body['transactionId']
        transaction_platform = body['transactionPlatform']
        logger.info('closing transaction id: {}, platform: {}'.format(transaction_id, transaction_platform))
    except KeyError:
        return api_response.client_error("Cannot read property 'transactionId' or 'transactionPlatform' from path parameters. ")

    # Check if the transaction id exists
    try:
        response = transactions_table.get_item(
            Key={
                'TransactionId': transaction_id,
                'TransactionPlatform': transaction_platform
            }
        )
    except ClientError as e:
        logger.info(e.response['Error']['Message'])
        return api_response.internal_error(e.response['Error']['Message'])
    if 'Item' not in response or not response['Item']:
        return api_response.not_found("TransactionId {} doesn't exist".format(transaction_id))

    # Update the StatusCode of the transaction.
    # Currently, it doesn't check for current StatusCode. Simply overrides the status to open
    transactions_table.update_item(
        Key={
            'TransactionId': transaction_id,
            'TransactionPlatform': transaction_platform
        },
        UpdateExpression="set StatusCode = :s",
        ExpressionAttributeValues={
            ':s': constants.TransactionStatusCode.open
        }
    )

    logger.info("Transaction [ id: {}, platform: {} ] re-opened successfully".format(transaction_id, transaction_platform))
    return api_response.ok_no_data("Transaction [ id: {}, platform: {} ] re-opened successfully".format(transaction_id, transaction_platform))


