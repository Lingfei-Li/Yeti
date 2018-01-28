import logging
from botocore.exceptions import ClientError
from datetime import datetime
from decimal import Decimal

from yeti_dynamodb import tokens_table
from yeti_auth_authorizers import OutlookAuthorizer, GmailAuthorizer
import yeti_constants as constants
import yeti_exceptions

logger = logging.getLogger("YetiAuthService")
logger.setLevel(logging.INFO)


def refresh_access_token(login_email):
    try:
        response = tokens_table.get_item(
            Key={
                'Email': login_email
            }
        )
    except ClientError as e:
        logger.info(e.response['Error']['Message'])
        raise yeti_exceptions.YetiApiInternalErrorException(e.response['Error']['Message'])

    if 'Item' not in response or not response['Item']:
        raise yeti_exceptions.YetiApiClientErrorException("Required login email does not exist")

    item = response['Item']

    if 'RefreshToken' not in item or not item['RefreshToken']:
        logger.info("Refresh token doesn't exist for the required access token")
        raise yeti_exceptions.YetiApiClientErrorException("Refresh token doesn't exist for the required access token")
    old_refresh_token = item['RefreshToken']

    if 'AuthType' not in item or not item['AuthType']:
        domain = login_email.strip().split("@")[1]
        if domain == 'gmail.com':
            auth_type = 'oauth-gmail'
        elif domain == 'outlook.com':
            auth_type = 'oauth-outlook'
        else:
            logger.info("AuthType is not defined for email {}. Cannot determine auth type from its domain {}.".format(login_email, domain))
            raise yeti_exceptions.YetiApiInternalErrorException("Cannot determine OAuth type of the login email: {}".format(login_email))
    else:
        auth_type = item['AuthType']

    if auth_type == 'oauth-outlook':
        # Get a new access token and a new refresh with the old refresh token
        # The new tokens will be saved to DB by the helper
        new_access_token = refresh_outlook_access_token_helper(login_email, old_refresh_token)
    elif auth_type == 'oauth-gmail':
        # Get a new access token, but the refresh stays the same
        from oauth2client.client import OAuth2Credentials
        if "JSONRepresentation" not in item or not item['JSONRepresentation']:
            raise yeti_exceptions.YetiApiInternalErrorException("JSON Representation is missing from Gmail OAuth token")
        json_representation = item['JSONRepresentation']
        google_api_credentials = OAuth2Credentials.from_json(json_representation)
        new_access_token = refresh_gmail_access_token_helper(login_email, google_api_credentials, old_refresh_token)
    else:
        raise yeti_exceptions.YetiApiInternalErrorException("AuthType {} is not supported.".format(auth_type))

    return new_access_token


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
        raise yeti_exceptions.YetiApiInternalErrorException("An error occurred authenticating user login request. Failed to retrieve auth verification result")
    elif auth_verify_result.code != constants.AuthVerifyResultCode.success:
        logger.info("Failed to get new token with refresh token. Code: {}, Message: {}".format(auth_verify_result.code, auth_verify_result.message))
        raise yeti_exceptions.YetiApiInternalErrorException("Failed to get new token with refresh token. Code: {}, Message: {}".format(auth_verify_result.code, auth_verify_result.message))

    oauth_credentials = auth_verify_result.credentials
    new_access_token = oauth_credentials.access_token
    new_refresh_token = oauth_credentials.refresh_token
    new_expiration_unix_timestamp = oauth_credentials.expiration_unix_timestamp

    if new_expiration_unix_timestamp < datetime.now().timestamp():
        logger.info("AccessToken already expired when retrieved from authCode")
        raise yeti_exceptions.YetiApiInternalErrorException("AccessToken already expired when retrieved from refresh token")

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

    return new_access_token


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
        raise yeti_exceptions.YetiApiInternalErrorException("An error occurred authenticating user login request. Failed to retrieve auth verification result")
    elif auth_verify_result.code != constants.AuthVerifyResultCode.success:
        logger.info("Failed to get new token with refresh token. Code: {}, Message: {}".format(auth_verify_result.code, auth_verify_result.message))
        raise yeti_exceptions.YetiApiInternalErrorException("Failed to get new token with refresh token. Code: {}, Message: {}".format(auth_verify_result.code, auth_verify_result.message))

    oauth_credentials = auth_verify_result.credentials
    new_access_token = oauth_credentials.access_token
    new_expiration_unix_timestamp = oauth_credentials.expiration_unix_timestamp
    google_api_credentials = oauth_credentials.raw_credentials_obj

    if new_expiration_unix_timestamp < datetime.now().timestamp():
        logger.info("AccessToken already expired when retrieved from authCode")
        raise yeti_exceptions.YetiApiInternalErrorException("AccessToken already expired when retrieved from refresh token")

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

    return new_access_token


def get_access_token_for_email(email):
    """ Retrieve the stored access token for the given email

    :param email: the email address of the user
    :return: new_access_token
    :raise: yeti_exceptions.YetiAuthTokenExpiredException
    :raise: yeti_exceptions.InternalErrorException
    """

    logger.info("Get access token for email: {}".format(email))
    try:
        response = tokens_table.get_item(Key={'Email': email})
    except ClientError as e:
        logger.error("Encountered ClientError while retrieving access token for email: {}. Error: {}".format(email, e.response['Error']['Message']))
        raise yeti_exceptions.YetiApiInternalErrorException("Encountered ClientError while retrieving access token for email: {}. Error: {}".format(email,
                                                                                                                                                    e.response['Error']['Message']))
    if 'Item' not in response or not response['Item']:
        logger.info("Email {} doesn't exist in tokens table".format(email))
        raise yeti_exceptions.YetiApiInternalErrorException("Email {} doesn't exist in tokens table".format(email))
    if 'AccessToken' not in response['Item']:
        logger.info("AccessToken is missing for email {}".format(email))
        raise yeti_exceptions.YetiApiInternalErrorException("AccessToken is missing for email {}".format(email))
    if 'ExpirationUnixTimestamp' not in response['Item']:
        logger.info("ExpirationUnixTimestamp is missing for email {}".format(email))
        raise yeti_exceptions.YetiApiInternalErrorException("ExpirationUnixTimestamp is missing for email {}".format(email))

    # Check expiration
    if response['Item']['ExpirationUnixTimestamp'] <= datetime.now().timestamp():
        raise yeti_exceptions.YetiAuthTokenExpiredException()

    # TODO: more sophisticated Gmail OAuth token expiration check using Google SDK

    return response['Item']['AccessToken']

# TODO: move OAuth logic from API to here
