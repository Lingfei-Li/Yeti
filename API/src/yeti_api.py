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
    elif auth_verify_result.code != constants.AuthVerifyResultCode.success:
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
        "Email": user_email,
        'AccessToken': access_token,
        'RefreshToken': refresh_token,
        'StatusCode': constants.AccessTokenStatusCode.valid,
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

        response = {
            'message': 'Outlook OAuth success',
            'loginEmail': user_email,
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
    error_response, login_email = auth_non_login_event(event)
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
    error_response, login_email = auth_non_login_event(event)
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


def refresh_access_token(event, context):
    """ Lambda handler for access token refresh API
    Args:
        event, context
            Standard Lambda handler arguments.
            Expects event['body'] to be non-None and is JSON parsable. Expects 'loginEmail' and 'accessToken' to be set in the body.
    Returns:
        response
            The response returned to the API. The new access token can be found at response['accessToken']
    """
    logger.debug("Got an token refresh request")
    try:
        body = json.loads(event['body'])
    except (KeyError, TypeError, ValueError):  # By default Lambda sets empty request body to None -> TypeError
        logger.info("Cannot parse request body to JSON object. ")
        return api_response.client_error("Cannot parse request body to JSON object. ")

    try:
        login_email = body['loginEmail']
        old_access_token = body['accessToken']
    except KeyError:
        return api_response.client_error("Cannot read property 'loginEmail' or 'accessToken' from the request body. ")

    try:
        response = tokens_table.get_item(
            Key={
                'Email': login_email
            }
        )
    except ClientError as e:
        logger.info(e.response['Error']['Message'])
        return api_response.internal_error(e.response['Error']['Message'])

    if 'Item' not in response or not response['Item']:
        return api_response.not_found("Required login email does not exist")
    else:
        item = response['Item']

    if 'RefreshToken' not in item or not item['RefreshToken']:
        logger.info("Refresh token doesn't exist for the required access token")
        return api_response.internal_error("Refresh token doesn't exist for the required access token")
    old_refresh_token = item['RefreshToken']

    if old_access_token != item['AccessToken']:
        return api_response.client_error("Provided access token doesn't match with the record in database")

    # Get a new token with the old refresh token
    # The new tokens will be saved to DB by the helper
    error_response, new_access_token = refresh_access_token_helper(old_refresh_token)
    if error_response:
        return error_response

    response = {
        'message': 'Token refreshed successfully',
        'accessToken': new_access_token
    }

    logger.info("Sending response: {}".format(response))
    return api_response.ok(response)


def refresh_access_token_helper(old_refresh_token):
    """ Get a new access token (Outlook OAuth) with the provided refresh token
    Args:
        old_refresh_token
            The refresh token used to get the new token
    Returns:
        error_response, new_access_token
            The first returned value is the API response constructed for error scenarios. A non-None value means there's an error that stops processing
            The second return value is the actual new access token. The value is only set if the error_response is None.
    """
    auth_verify_result = OutlookAuthorizer.refresh_token(old_refresh_token)

    if not auth_verify_result:
        logger.info("An error occurred authenticating user login request. Failed to retrieve auth verification result")
        return api_response.internal_error("An error occurred authenticating user login request. Failed to retrieve auth verification result"), None
    elif auth_verify_result.code != constants.AuthVerifyResultCode.success:
        logger.info("Failed to get new token with refresh token. Code: {}, Message: {}".format(auth_verify_result.code, auth_verify_result.message)), None
        return api_response.client_error("Failed to get new token with refresh token. Code: {}, Message: {}".format(auth_verify_result.code, auth_verify_result.message)), None

    auth_result_data = auth_verify_result.data
    new_access_token = auth_result_data['access_token']
    new_refresh_token = auth_result_data['refresh_token']
    new_expires_in = auth_result_data['expires_in']
    new_expiration_unix_timestamp = datetime.now().timestamp() + new_expires_in - 300  # current time + expiration - 5 minutes

    if new_expiration_unix_timestamp < datetime.now().timestamp():
        logger.info("AccessToken already expired when retrieved from authCode")
        return api_response.internal_error("AccessToken already expired when retrieved from refresh token"), None

    user = outlook_service.get_me(new_access_token)
    user_email = None
    if 'mail' in user and user['mail'] and re.match(r"[^@]+@[^@]+\.[^@]+", user['mail']):
        user_email = user['mail']
    if 'userPrincipalName' in user and user['userPrincipalName'] and re.match(r"[^@]+@[^@]+\.[^@]+", user['userPrincipalName']):
        user_email = user['userPrincipalName']
    if not user_email:
        logger.error("Cannot determine user email. Auth result: {}".format(auth_result_data))
        return api_response.internal_error("Cannot determine user email. Refresh token result: {}. Get user response: {}".format(auth_result_data, user)), None

    # Save the new token to DDB
    logger.info("Saving new token to database")
    tokens_table.put_item(Item={
        'AccessToken': new_access_token,
        "Email": user_email,
        'RefreshToken': new_refresh_token,
        'StatusCode': constants.AccessTokenStatusCode.valid,
        'ExpirationUnixTimestamp': Decimal(new_expiration_unix_timestamp)
    })

    return None, new_access_token


def auth_non_login_event(event):
    logger.info("Request Object: {}".format(event))
    logger.info("Request Header: {}".format(event['headers']))
    try:
        authorization_header = event['headers']['Authorization']
    except (KeyError, TypeError):
        return api_response.client_error("Cannot read property 'Authorization' from request header"), None

    try:
        login_email = event['headers']['login-email']
    except (KeyError, TypeError):
        return api_response.client_error("Cannot read property 'login-email' or 'loginemail' from request header"), None

    authorization_components = authorization_header.split(" ")
    if len(authorization_components) == 0 or authorization_components[0] != 'Bearer':
        return api_response.client_error("Only 'Bearer' header type for Authorization is supported. Please set the Authorization header to 'Bearer <token>'"), None
    if len(authorization_components) < 2 or not authorization_components[1]:
        return api_response.client_error("Authorization token cannot be found"), None

    token = authorization_components[1]

    auth_verify_result = LoginAuthorizer.verify_jwt_token(login_email=login_email, token=token)

    if not auth_verify_result:
        return api_response.internal_error("An error occurred when verifying token. Failed to retrieve auth verification result"), None
    elif auth_verify_result.code != constants.AuthVerifyResultCode.success:
        return api_response.client_error("Permission Denied. Code: {}, Message: {}".format(auth_verify_result.code, auth_verify_result.message)), None

    return None, login_email

