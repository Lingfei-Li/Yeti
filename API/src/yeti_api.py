import logging
import json
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from datetime import datetime
import re
from decimal import Decimal
from uuid import uuid4

import api_response as api_response
from dynamodb import transactions_table, logins_table, tokens_table
from utils import replace_decimals
from auth import LoginAuthorizer, OutlookAuthorizer
import constants as constants
import outlook_service

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def login_outlook_oauth(event, context):
    logger.debug("Got an outlook auth request")
    try:
        body = json.loads(event['body'])
    except (KeyError, TypeError, ValueError):  # By default Lambda sets the body to None if it's left empty -> TypeError
        logger.info("Cannot parse request body to JSON object. ")
        return api_response.client_error("Cannot parse request body to JSON object. ")

    try:
        auth_code = body['authCode']
        logger.debug('authCode: {}'.format(auth_code))
    except KeyError:
        return api_response.client_error("Cannot read property 'authCode' from the request body. ")

    auth_verify_result = OutlookAuthorizer.outlook_oauth(auth_code)

    if not auth_verify_result:
        logger.info("An error occurred authenticating user login request. Failed to retrieve auth verification result")
        return api_response.internal_error("An error occurred authenticating user login request. Failed to retrieve auth verification result")
    elif auth_verify_result.code != constants.AuthVerifyResultCodes.success:
        logger.info("Permission Denied. Code: {}, Message: {}".format(auth_verify_result.code, auth_verify_result.message))
        return api_response.client_error("Permission Denied. Code: {}, Message: {}".format(auth_verify_result.code, auth_verify_result.message))

    auth_result_data = auth_verify_result.data
    access_token = auth_result_data['access_token']
    refresh_token = auth_result_data['refresh_token']
    expires_in = auth_result_data['expires_in']
    expiration_unix_timestamp = datetime.now().timestamp() + expires_in - 300  # current time + expiration - 5 minutes

    if expiration_unix_timestamp < datetime.now().timestamp():
        logger.info("AccessToken already expired when retrieved from authCode")
        return api_response.internal_error("AccessToken already expired when retrieved from authCode")

    user = outlook_service.get_me(access_token)
    user_email = None
    if 'mail' in user and user['mail'] and re.match(r"[^@]+@[^@]+\.[^@]+", user['mail']):
        user_email = user['mail']
    if 'userPrincipalName' in user and user['userPrincipalName'] and re.match(r"[^@]+@[^@]+\.[^@]+", user['userPrincipalName']):
        user_email = user['userPrincipalName']
    if not user_email:
        logger.error("Cannot determine user email. Auth result: {}".format(auth_result_data))
        return api_response.internal_error("Cannot determine user email. Auth result: {}".format(auth_result_data))

    # TODO: save token to DDB
    tokens_table.put_item(Item={
        'AccessToken': access_token,
        "Email": user_email,
        'RefreshToken': refresh_token,
        'ExpirationUnixTimestamp': Decimal(expiration_unix_timestamp)
    })

    # Check if email exists.
    #  If no, create an entry for the email with an UUID secret.
    #  Create a jwt and return it to front end
    try:
        response = logins_table.get_item(
            Key={
                'Email': user_email
            }
        )
    except ClientError as e:
        logger.info(e.response['Error']['Message'])
        return api_response.internal_error(e.response['Error']['Message'])
    else:
        if 'Item' not in response or not response['Item']:
            item = {
                "Email": user_email
            }
        else:
            item = response['Item']
        secret = str(uuid4())
        if 'Secret' not in item or not item['Secret']:
            item['Secret'] = secret
        logger.info("Constructed logins data item: {}".format(item))

        response = logins_table.put_item(
            Item=item
        )
        logger.info("Successfully put logins data with response: {}".format(response))

        # TODO: Trigger email processor to refresh email

        response = {
            'message': 'Outlook OAuth success',
            'user_email': user_email,
            'token': LoginAuthorizer.generate_jwt_token(login_email=user_email, secret=secret)
        }

        return api_response.ok(response)


def login(event, context):
    # TODO: retrieve the email and token from request. verify if the token exists for the email
    # TODO: If token exists in the expired tokens, issue a valid token back to the client
    # TODO: If no valid token exists for the email, get a refreshed token with the old token and return the new token

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
