import re
import datetime

import aws_client_dynamodb
import outlook_service
import yeti_logging
import yeti_models
from yeti_models import AuthVerifyResultCode
import yeti_exceptions
from yeti_utils_auth import OutlookAuthorizer

logger = yeti_logging.get_logger("YetiAuthService")


def oauth_login(auth_code):
    # Get access token with the auth code
    auth_verify_result = OutlookAuthorizer.exchange_code_for_credentials(auth_code)
    if auth_verify_result.code != AuthVerifyResultCode.success:
        raise yeti_exceptions.OutlookApiErrorException("failed to exchange code for access token. Code: {}, Message: {}".format(auth_verify_result.code, auth_verify_result.message))

    oauth_credentials = auth_verify_result.credentials
    access_token = oauth_credentials.access_token
    refresh_token = oauth_credentials.refresh_token
    expiry_datetime = oauth_credentials.expiry_datetime

    # Get user email with access token from outlook service
    user = outlook_service.get_me(access_token)
    user_email = None
    if 'EmailAddress' in user and user['EmailAddress'] and re.match(r"[^@]+@[^@]+\.[^@]+", user['EmailAddress']):
        user_email = user['EmailAddress']
    if not user_email:
        raise yeti_exceptions.OutlookApiErrorException("Cannot determine user email. Auth result: {}".format(auth_verify_result))

    # Create auth item to prepare for DDB persistence
    auth_item = yeti_models.Auth.build(email=user_email,
                                       access_token=access_token,
                                       refresh_token=refresh_token,
                                       token_expiry_datetime=expiry_datetime,
                                       auth_method='oauth_outlook'
                                       )

    # Save or update token in DDB
    if aws_client_dynamodb.AuthServiceAuthTable.is_exist(user_email):
        logger.info('Email already exists in Auth table. Updating tokens')
        aws_client_dynamodb.AuthServiceAuthTable.update_auth_item_tokens(email=user_email,
                                                                         access_token=access_token,
                                                                         refresh_token=refresh_token,
                                                                         token_expiry_datetime=expiry_datetime)
    else:
        logger.info('Email does not exist. Creating new auth item.')
        aws_client_dynamodb.AuthServiceAuthTable.put_auth_item(auth_item)

    return auth_item


def refresh_access_token(user_email, old_refresh_token=None, auth_type=None):
    if old_refresh_token is None:
        auth_item = aws_client_dynamodb.AuthServiceAuthTable.get_auth_item(user_email)
        old_refresh_token = auth_item.refresh_token
        auth_type = auth_item.auth_type

    if auth_type is None:
        domain = user_email.strip().split("@")[1]
        if domain == 'outlook.com':
            auth_type = 'oauth-outlook'
        else:
            raise yeti_exceptions.YetiApiInternalErrorException("Cannot determine OAuth type of the login email: {}".format(user_email))

    if auth_type == 'oauth-outlook':
        # Get a new access token and a new refresh with the old refresh token
        # The new tokens will be saved to DB by the helper
        auth_verify_result = OutlookAuthorizer.refresh_token(old_refresh_token)

        if not auth_verify_result:
            raise yeti_exceptions.YetiApiInternalErrorException("An error occurred authenticating user login request. Failed to retrieve auth verification result")
        elif auth_verify_result.code != yeti_models.AuthVerifyResultCode.success:
            raise yeti_exceptions.YetiApiInternalErrorException("Failed to get new token with refresh token. Code: {}, Message: {}".format(auth_verify_result.code, auth_verify_result.message))

        oauth_credentials = auth_verify_result.credentials
        new_access_token = oauth_credentials.access_token
        new_refresh_token = oauth_credentials.refresh_token
        new_expiry_datetime = oauth_credentials.expiry_datetime

        # Update the new token in DB
        aws_client_dynamodb.AuthServiceAuthTable.update_auth_item_tokens(user_email, new_access_token, new_refresh_token, new_expiry_datetime)

        return new_access_token
    else:
        raise yeti_exceptions.YetiApiInternalErrorException("AuthType {} is not supported.".format(auth_type))


def get_access_token_for_email(email):
    """ Retrieve the stored access token for the given email. Refresh the access token if necessary """

    logger.info("Get access token for email: {}".format(email))

    auth_item = aws_client_dynamodb.AuthServiceAuthTable.get_auth_item(email)

    # Check expiration. Refresh the token when appropriate
    if auth_item.token_expiry_datetime < datetime.datetime.now(auth_item.token_expiry_datetime.tzinfo):
        logger.info('Current access token is expired. Refreshing')
        auth_item.access_token = refresh_access_token(email, auth_item.refresh_token, auth_item.auth_type)

    return auth_item.access_token


def get_outlook_notification_subscription_for_email(email):
    """ Get the subscription id for outlook notification subscription """

    logger.info("Get subscription id for email: {}".format(email))

    auth_item = aws_client_dynamodb.AuthServiceAuthTable.get_auth_item(email)

    return auth_item.outlook_notification_subscription_id, auth_item.outlook_notification_subscription_expiry_datetime




