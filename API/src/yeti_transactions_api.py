import logging
import json
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
import traceback

import yeti_api_response as api_response
from yeti_dynamodb import transactions_table
from yeti_common_utils import replace_decimals
from yeti_auth_authorizers import LoginAuthorizer
import yeti_constants as constants
import yeti_email_service
import yeti_auth_service
import yeti_exceptions


logger = logging.getLogger("YetiTransactionsApi")
logger.setLevel(logging.INFO)


def load_transactions(event, context):
    error_response, login_email = LoginAuthorizer.auth_non_login_event(event)
    if error_response is not None:
        return error_response

    logger.info("Loading transactions for {}".format(login_email))

    try:
        try:
            logger.info("Retrieve and examine access token for email")
            access_token = yeti_auth_service.get_access_token_for_email(login_email)
            logger.info("Load and transform emails")
            yeti_email_service.transform_emails_util(access_token, login_email)
        except yeti_exceptions.YetiAuthTokenExpiredException:
            logger.info("Access token expired. Trying to refresh")
            access_token = yeti_auth_service.refresh_access_token(login_email)
            logger.info("Token refreshed. Load and transform emails")
            yeti_email_service.transform_emails_util(access_token, login_email)

        # Only return transactions sent to the login email
        filter_expression = Key('UserEmail').eq(login_email)

        response = transactions_table.scan(
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

    except yeti_exceptions.YetiApiClientErrorException as e:
        logger.error("Error transforming emails: {}".format(e))
        logger.error(traceback.format_exc())
        return api_response.client_error("Error transforming emails: {}".format(e))
    except yeti_exceptions.YetiApiInternalErrorException as e:
        logger.error("Error transforming emails: {}".format(e))
        logger.error(traceback.format_exc())
        return api_response.internal_error("Error transforming emails: {}".format(e))
    except Exception as e:
        logger.error("Error transforming emails. Encountered unexpected error: {}".format(e))
        logger.error(traceback.format_exc())
        return api_response.internal_error("Error transforming emails. Encountered unexpected error: {}".format(e))


def get_transaction_details(event, context):
    error_response, login_email = LoginAuthorizer.auth_non_login_event(event)
    if error_response is not None:
        return error_response

    try:
        transaction_platform = event['pathParameters']['transactionPlatform']
        transaction_id = event['pathParameters']['transactionId']
    except Exception as e:
        return api_response.client_error("transactionPlatform or transactionId is not present in the request. Please check your input. Error: {}".format(e))

    try:
        response = transactions_table.get_item(
            Key={
                'TransactionId': transaction_id,
                'TransactionPlatform': transaction_platform
            }
        )
    except ClientError as e:
        logger.error(e.response['Error']['Message'])
        return api_response.internal_error(e.response['Error']['Message'])
    if 'Item' not in response or not response['Item']:
        return api_response.not_found("TransactionId {} at TransactionPlatform {} doesn't exist".format(transaction_id, transaction_platform))

    result_data = replace_decimals(response['Item'])

    return api_response.ok(result_data)


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
        logger.error(e.response['Error']['Message'])
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
        logger.error(e.response['Error']['Message'])
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

