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

    # Save token to DDB
    tokens_table.put_item(Item={
        'AccessToken': access_token,
        "Email": user_email,
        'RefreshToken': refresh_token,
        'ExpirationUnixTimestamp': Decimal(expiration_unix_timestamp)
    })

    # Check if it's first time that this email logins
    #  If yes, create an entry for the email with an UUID secret.
    #  Otherwise, obtain the secret from the data item
    # Create a jwt and return it to front end
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
                "Email": user_email,
                "Secret": str(uuid4())
            }
            logger.info("Constructed logins data item for first-time login: {}".format(item))

            response = logins_table.put_item(
                Item=item
            )
            logger.info("Successfully put logins data with response: {}".format(response))
        else:
            item = response['Item']
        if 'Secret' not in item or not item['Secret']:
            logger.error("Email {} exists but doesn't have a secret".format(user_email))
            return api_response.internal_error("Cannot find secret for email {}".format(user_email))

        # TODO: Trigger email processor to refresh email

        response = {
            'message': 'Outlook OAuth success',
            'login_email': user_email,
            'token': LoginAuthorizer.generate_jwt_token(login_email=user_email, secret=item['Secret'])
        }

        logger.info("Sending response: {}".format(response))
        return api_response.ok(response)


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
        authorization_header = event['headers']['Authorization']
    except (KeyError, TypeError):
        return api_response.client_error("Cannot read property 'Authorization' from request header"), None

    try:
        login_email = event['headers']['LoginEmail']
    except (KeyError, TypeError):
        return api_response.client_error("Cannot read property 'LoginEmail' from request header"), None

    authorization_components = authorization_header.split(" ")
    if len(authorization_components) == 0 or authorization_components[0] != 'Bearer':
        return api_response.client_error("Only 'Bearer' header type for Authorization is supported. Please set the Authorization header to 'Bearer <token>'"), None
    if len(authorization_components) < 2 or not authorization_components[1]:
        return api_response.client_error("Authorization token cannot be found"), None

    token = authorization_components[1]

    auth_verify_result = LoginAuthorizer.verify_jwt_token(login_email=login_email, token=token)

    if not auth_verify_result:
        return api_response.internal_error("An error occurred when verifying token. Failed to retrieve auth verification result"), None
    elif auth_verify_result.code != constants.AuthVerifyResultCodes.success:
        return api_response.client_error("Permission Denied. Code: {}, Message: {}".format(auth_verify_result.code, auth_verify_result.message)), None

    return None, login_email
