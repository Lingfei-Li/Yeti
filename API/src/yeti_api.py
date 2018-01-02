import logging
import json
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

import src.api_response as api_response
from src.dynamodb import transactions_table
from src.utils import replace_decimals
from src.auth import Authorizer
import src.constants as constants

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def login(event, context):
    try:
        body = json.loads(event['body'])
    except (KeyError, TypeError, ValueError):  # By default Lambda sets the body to None if it's left empty -> TypeError
        return api_response.client_error("Cannot parse request body to JSON object. ")

    try:
        login_email = body['loginEmail']
        password_hash = body['passwordHash']
    except KeyError:
        return api_response.client_error("Cannot read property 'loginEmail' or 'passwordHash' from the request body. ")

    auth_verify_result = Authorizer.verify_email_password(login_email, password_hash)

    if not auth_verify_result:
        return api_response.internal_error("An error occurred authenticating user login request. Failed to retrieve auth verification result")
    elif auth_verify_result.code != constants.AuthVerifyResultCodes.success:
        return api_response.client_error("Permission Denied. Code: {}, Message: {}".format(auth_verify_result.code, auth_verify_result.message))

    return api_response.ok({"message": "Email-Password login auth validated", "token": auth_verify_result.token})


def load_transactions(event, context):
    print(event)
    error_response, login_email = auth_non_login_event(event)
    if error_response is not None:
        return error_response

    # Only return transactions sent to the login email
    filter_expression = Key('ReceiverEmail').eq(login_email)

    response = transactions_table.scan(
        ProjectionExpression="SenderFirstName, SenderLastName, SenderEmail, Amount, TransactionUnixTimestamp, #_Status, TransactionType",
        ExpressionAttributeNames={"#_Status": "Status"},
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
    # Auth
    if 'headers' not in event or event['headers'] is None \
            or 'Authorization' not in event['headers'] or not event['headers']['Authorization']:
        return api_response.client_error("No 'Authorization' set in request headers")

    token = event['headers']['Authorization']
    auth_verify_result = Authorizer.verify_token(token=token)
    if not auth_verify_result:
        return api_response.internal_error("An error occurred when verifying token. Failed to retrieve auth verification result")
    elif auth_verify_result.code != constants.AuthVerifyResultCodes.success:
        return api_response.client_error("Permission Denied. Code: {}, Message: {}".format(auth_verify_result.code, auth_verify_result.message))
    # Auth Complete

    payload = auth_verify_result.data
    if not payload or 'login_email' not in payload or not payload['login_email']:
        return api_response.client_error("'login_email' is missing from the token")
    login_email = payload['login_email']

    if 'pathParameters' not in event or not event['pathParameters'] or 'transactionId' not in event['pathParameters'] \
            or event['pathParameters']['transactionId']:
        return api_response.client_error("No 'transactionId' set in path parameters")
    transaction_id = event['pathParameters']['transactionId']

    try:
        response = transactions_table.get_item(
            Key={
                "TransactionId": transaction_id
            }
        )
    except ClientError as e:
        return api_response.internal_error(e.response['Error']['Message'])
    else:
        item = response['Item']
        status = item['Status']
        if item['ReceiverEmail'] != login_email:
            return api_response.client_error("Permission denied")
        if status == "suspended":
            return api_response.client_error("The transaction is in suspended status and cannot be closed.")
        elif status != "closed":
            transactions_table.update_item(
                Key={
                    'TransactionId': transaction_id
                },
                UpdateExpression="set Status = :s",
                ExpressionAttributeValues={
                    ':s': "closed",
                }
            )
    return api_response.ok_no_data("Transaction closed")


def auth_non_login_event(event):
    try:
        token = event['headers']['Authorization']
    except (KeyError, TypeError):
        return api_response.client_error("Cannot read property 'Authorization' from request header"), None

    auth_verify_result = Authorizer.verify_token(token=token)

    if not auth_verify_result:
        return api_response.internal_error("An error occurred when verifying token. Failed to retrieve auth verification result"), None
    elif auth_verify_result.code != constants.AuthVerifyResultCodes.success:
        return api_response.client_error("Permission Denied. Code: {}, Message: {}".format(auth_verify_result.code, auth_verify_result.message)), None
    payload = auth_verify_result.data
    if not payload or 'login_email' not in payload or not payload['login_email']:
        return api_response.client_error("'login_email' is missing from the token"), None

    return None, payload['login_email']
