import logging
import json
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

import api_response as api_response
from dynamodb import transactions_table
from utils import replace_decimals
from auth import Authorizer, OutlookAuthorizer
import constants as constants
import outlook_service
import re

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def login_outlook_oauth(event, context):
    try:
        body = json.loads(event['body'])
    except (KeyError, TypeError, ValueError):  # By default Lambda sets the body to None if it's left empty -> TypeError
        return api_response.client_error("Cannot parse request body to JSON object. ")

    try:
        auth_code = body['authCode']
    except KeyError:
        return api_response.client_error("Cannot read property 'authCode' from the request body. ")

    auth_verify_result = OutlookAuthorizer.outlook_oauth(auth_code)

    if not auth_verify_result:
        return api_response.internal_error("An error occurred authenticating user login request. Failed to retrieve auth verification result")
    elif auth_verify_result.code != constants.AuthVerifyResultCodes.success:
        return api_response.client_error("Permission Denied. Code: {}, Message: {}".format(auth_verify_result.code, auth_verify_result.message))

    auth_result_data = auth_verify_result.data
    access_token = auth_result_data['access_token']
    refresh_token = auth_result_data['refresh_token']
    expires_in = auth_result_data['expires_in']

    user = outlook_service.get_me(access_token)
    user_email = None
    if 'mail' in user and user['mail'] and re.match(r"[^@]+@[^@]+\.[^@]+", user['mail']):
        user_email = user['mail']
    if 'userPrincipalName' in user and user['userPrincipalName'] and re.match(r"[^@]+@[^@]+\.[^@]+", user['userPrincipalName']):
        user_email = user['userPrincipalName']
    if not user_email:
        return api_response.internal_error("Cannot determine user email. Auth result: {}".format(auth_result_data))

    # TODO: Trigger email processor to refresh email

    response_data = {
        'message': 'Outlook OAuth success',
        'access_token': access_token,
        'user_email': user_email,
        'refresh_token': refresh_token,
        'expires_in': expires_in
    }

    return api_response.ok(response_data)


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
