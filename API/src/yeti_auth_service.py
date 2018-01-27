import logging
import json
from botocore.exceptions import ClientError
from datetime import datetime
import re
from decimal import Decimal
from uuid import uuid4

import yeti_api_response as api_response
from yeti_dynamodb import logins_table, tokens_table
from yeti_auth_authorizers import LoginAuthorizer, OutlookAuthorizer, GmailAuthorizer
import yeti_constants as constants
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
        'ExpirationUnixTimestamp': Decimal(expiration_unix_timestamp),
        'AuthType': 'oauth-outlook'
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


def refresh_access_token(event, context):
    """ Lambda handler for access token refresh API for all types of OAuth (Outlook, Gmail...)
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

    item = response['Item']

    if 'RefreshToken' not in item or not item['RefreshToken']:
        logger.info("Refresh token doesn't exist for the required access token")
        return api_response.internal_error("Refresh token doesn't exist for the required access token")
    old_refresh_token = item['RefreshToken']

    if old_access_token != item['AccessToken']:
        return api_response.client_error("Provided access token doesn't match with the record in database")

    if 'AuthType' not in item or not item['AuthType']:
        domain = login_email.strip().split("@")[1]
        if domain == 'gmail.com':
            auth_type = 'oauth-gmail'
        elif domain == 'outlook.com':
            auth_type = 'oauth-outlook'
        else:
            logger.info("AuthType is not defined for email {}. Cannot determine auth type from its domain {}.".format(login_email, domain))
            return api_response.internal_error("Cannot determine OAuth type of the login email: {}".format(login_email))
        logger.info("AuthType is not defined for email {}. Using email domain to derive auth type: {}".format(login_email, auth_type))

    auth_type = item['AuthType']
    if auth_type == 'oauth-outlook':
        # Get a new token with the old refresh token
        # The new tokens will be saved to DB by the helper
        error_response, new_access_token = refresh_outlook_access_token_helper(login_email, old_refresh_token)
        if error_response:
            return error_response
    elif auth_type == 'oauth-gmail':
        from oauth2client.client import OAuth2Credentials
        try:
            google_api_credentials = OAuth2Credentials.from_json(item['JSONRepresentation'])
        except Exception as e:
            logger.info("Failed to deserialize oauth2client from JSON representation. Error: {}".format(e))
            return api_response.internal_error("Failed to deserialize oauth2client from JSON representation. Error: {}".format(e))

        error_response, new_access_token = refresh_gmail_access_token_helper(login_email, google_api_credentials, old_refresh_token)
        if error_response:
            return error_response
    else:
        logger.info("AuthType {} is not supported.".format(auth_type))
        return api_response.internal_error("AuthType {} is not supported.".format(auth_type))

    response = {
        'message': 'Token refreshed successfully',
        'accessToken': new_access_token
    }

    logger.info("Sending response: {}".format(response))
    return api_response.ok(response)


def refresh_outlook_access_token_helper(user_email, old_refresh_token):
    """ Get a new access token (Outlook OAuth) with the provided refresh token
    Args:
        user_email, old_refresh_token
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

    # Update the new token to DDB
    logger.info("Updating token in database")
    tokens_table.update_item(
        Key={
            'Email': user_email
        },
        UpdateExpression="set AccessToken=:t, RefreshToken=:r, StatusCode=:s, ExpirationUnixTimestamp=:e",
        ExpressionAttributeValues={
            ':t': new_access_token,
            ':r': new_refresh_token,
            ':s': constants.AccessTokenStatusCode.valid,
            ':e': Decimal(new_expiration_unix_timestamp)
        }
    )

    return None, new_access_token


def refresh_gmail_access_token_helper(user_email, google_api_credentials, refresh_token):
    """ Get a new access token (Outlook OAuth) with the provided refresh token
    Args:
        user_email, google_api_credentials, refresh_token
            An Google's oauth2client.client.AccessTokenCredentials credential object used to refresh tokens
            refresh_token is needed as the google_api_credentials might not have a refresh_token in its JSON representation (it's not the first Gmail login attempt for our APP)
    Returns:
        error_response, new_access_token
            The first returned value is the API response constructed for error scenarios. A non-None value means there's an error that stops processing
            The second return value is the actual new access token. The value is only set if the error_response is None.
    """
    google_api_credentials.refresh_token = refresh_token
    logger.info(google_api_credentials)
    auth_verify_result = GmailAuthorizer.refresh_token(google_api_credentials)

    if not auth_verify_result:
        logger.info("An error occurred authenticating user login request. Failed to retrieve auth verification result")
        return api_response.internal_error("An error occurred authenticating user login request. Failed to retrieve auth verification result"), None
    elif auth_verify_result.code != constants.AuthVerifyResultCode.success:
        logger.info("Failed to get new token with refresh token. Code: {}, Message: {}".format(auth_verify_result.code, auth_verify_result.message)), None
        return api_response.client_error("Failed to get new token with refresh token. Code: {}, Message: {}".format(auth_verify_result.code, auth_verify_result.message)), None

    oauth_credentials = auth_verify_result.credentials
    new_access_token = oauth_credentials.access_token
    new_expiration_unix_timestamp = oauth_credentials.expiration_unix_timestamp
    google_api_credentials = oauth_credentials.raw_credentials_obj

    if new_expiration_unix_timestamp < datetime.now().timestamp():
        logger.info("AccessToken already expired when retrieved from authCode")
        return api_response.internal_error("AccessToken already expired when retrieved from refresh token"), None

    # Update the new token to DDB
    logger.info("Updating token in database...")
    tokens_table.update_item(
        Key={
            'Email': user_email
        },
        UpdateExpression="set AccessToken=:t, StatusCode=:s, ExpirationUnixTimestamp=:e, JSONRepresentation=:j",
        ExpressionAttributeValues={
            ':t': new_access_token,
            ':s': constants.AccessTokenStatusCode.valid,
            ':e': Decimal(new_expiration_unix_timestamp),
            ':j': google_api_credentials.to_json()
        }
    )

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

    # Save/Update token to DDB
    try:
        response = tokens_table.get_item(
            Key={
                'Email': user_email
            }
        )
    except ClientError as e:
        logger.info(e.response['Error']['Message'])
        return api_response.internal_error(e.response['Error']['Message'])
    else:
        if 'Item' not in response or not response['Item']:
            if not refresh_token:
                # TODO: If the returned credentials and database token item doesn't contain refresh token, we may want to force request a refresh token, not simply throw an error.
                # https://developers.google.com/identity/protocols/OAuth2WebServer#formingtheurl
                return api_response.internal_error("Cannot determine refresh token for the email: {}. Cannot find refresh token in either oauth credential or database"
                                                   .format(user_email))
            tokens_table.put_item(Item={
                "Email": user_email,
                'AccessToken': access_token,
                'RefreshToken': refresh_token,
                'StatusCode': constants.AccessTokenStatusCode.valid,
                'ExpirationUnixTimestamp': Decimal(expiration_unix_timestamp),
                'AuthType': 'oauth-gmail',
                'JSONRepresentation': google_api_credentials.to_json()
            })
            logger.info("Successfully put token data")
        else:
            # Note: don't update refresh token
            tokens_table.update_item(
                Key={
                    'Email': user_email
                },
                UpdateExpression="set AccessToken=:t, StatusCode=:s, ExpirationUnixTimestamp=:e, JSONRepresentation=:j",
                ExpressionAttributeValues={
                    ':t': access_token,
                    ':s': constants.AccessTokenStatusCode.valid,
                    ':e': Decimal(expiration_unix_timestamp),
                    ':j': google_api_credentials.to_json()
                }
            )

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


