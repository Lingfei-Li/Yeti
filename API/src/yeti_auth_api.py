import logging
import json
from botocore.exceptions import ClientError
from datetime import datetime
import re
from decimal import Decimal
from uuid import uuid4

import api_response as api_response
from dynamodb import logins_table, tokens_table
from auth import LoginAuthorizer, OutlookAuthorizer, GmailAuthorizer
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

    auth_verify_result = OutlookAuthorizer.get_credentials(auth_code)

    if not auth_verify_result:
        logger.info("An error occurred authenticating user login request. Failed to retrieve auth verification result")
        return api_response.internal_error("An error occurred authenticating user login request. Failed to retrieve auth verification result")
    elif auth_verify_result.code != constants.AuthVerifyResultCode.success:
        logger.info("Permission Denied. Code: {}, Message: {}".format(auth_verify_result.code, auth_verify_result.message))
        return api_response.client_error("Permission Denied. Code: {}, Message: {}".format(auth_verify_result.code, auth_verify_result.message))

    oauth_credentials = auth_verify_result.credentials
    access_token = oauth_credentials.access_token
    refresh_token = oauth_credentials.refresh_token
    expiration_unix_timestamp = oauth_credentials.expiration_unix_timestamp

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
        logger.error("Cannot determine user email. Auth result: {}".format(auth_verify_result))
        return api_response.internal_error("Cannot determine user email. Auth result: {}".format(auth_verify_result))

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


def refresh_outlook_access_token(event, context):
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
    error_response, new_access_token = refresh_outlook_access_token_helper(old_refresh_token)
    if error_response:
        return error_response

    response = {
        'message': 'Token refreshed successfully',
        'accessToken': new_access_token
    }

    logger.info("Sending response: {}".format(response))
    return api_response.ok(response)


def refresh_outlook_access_token_helper(old_refresh_token):
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

    oauth_credentials = auth_verify_result.credentials
    new_access_token = oauth_credentials.access_token
    new_refresh_token = oauth_credentials.refresh_token
    new_expiration_unix_timestamp = oauth_credentials.expiration_unix_timestamp

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
        logger.error("Cannot determine user email. Auth result: {}".format(auth_verify_result))
        return api_response.internal_error("Cannot determine user email. Refresh token result: {}. Get user response: {}".format(auth_verify_result, user)), None

    # Save the new token to DDB
    logger.info("Saving new token to database")
    tokens_table.put_item(Item={
        'AccessToken': new_access_token,
        "Email": user_email,
        'RefreshToken': new_refresh_token,
        'StatusCode': constants.AccessTokenStatusCode.valid,
        'ExpirationUnixTimestamp': Decimal(new_expiration_unix_timestamp),
        'AuthType': 'oauth-outlook'
    })

    return None, new_access_token


def login_gmail_oauth(event, context):
    logger.debug("Got a gmail auth request")
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

    auth_verify_result = GmailAuthorizer.get_credentials(auth_code)

    if not auth_verify_result:
        logger.info("An error occurred authenticating user login request. Failed to retrieve auth verification result")
        return api_response.internal_error("An error occurred authenticating user login request. Failed to retrieve auth verification result")
    elif auth_verify_result.code != constants.AuthVerifyResultCode.success:
        logger.info("Permission Denied. Code: {}, Message: {}".format(auth_verify_result.code, auth_verify_result.message))
        return api_response.client_error("Permission Denied. Code: {}, Message: {}".format(auth_verify_result.code, auth_verify_result.message))

    oauth_credentials = auth_verify_result.credentials
    access_token = oauth_credentials.access_token
    refresh_token = oauth_credentials.refresh_token
    expiration_unix_timestamp = oauth_credentials.expiration_unix_timestamp
    google_api_credentials = oauth_credentials.raw_credentials_obj

    if expiration_unix_timestamp < datetime.now().timestamp():
        logger.info("AccessToken already expired when retrieved from authCode")
        return api_response.internal_error("AccessToken already expired when retrieved from authCode")

    user_email = GmailAuthorizer.get_user_email(google_api_credentials)
    if not user_email:
        logger.error("Cannot determine user email. Auth result: {}".format(auth_verify_result))
        return api_response.internal_error("Cannot determine user email. Auth result: {}".format(auth_verify_result))

    # Save token to DDB
    tokens_table.put_item(Item={
        "Email": user_email,
        'AccessToken': access_token,
        'RefreshToken': refresh_token,
        'StatusCode': constants.AccessTokenStatusCode.valid,
        'ExpirationUnixTimestamp': Decimal(expiration_unix_timestamp),
        'AuthType': 'oauth-gmail'
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