import jwt
import requests
import yeti_logging

import yeti_models
from secret_config import outlook_credentials
from yeti_models import AuthVerifyResult, AuthVerifyResultCode, OAuthCredentials

logger = yeti_logging.get_logger("YetiAuthUtils")


class OutlookAuthorizer:
    # Constant strings for OAuth2 flow
    # The OAuth authority
    authority = 'https://login.microsoftonline.com'

    # The authorize URL that initiates the OAuth2 client credential flow for admin consent
    authorize_url = '{0}{1}'.format(authority, '/common/oauth2/v2.0/authorize?{0}')

    # The token issuing endpoint
    token_url = '{0}{1}'.format(authority, '/common/oauth2/v2.0/token')

    """
    The redirect url must align with the redirect url used for signin
    """
    # test_redirect_url = 'http://localhost:8000/tutorial/gettoken/'
    redirect_url = 'http://localhost:8000/tutorial/gettoken/'
    # redirect_url = 'https://auth.expo.io/@drinkiit/yeti-mobile'

    # The scopes required by the app
    scopes = ['openid',
              'offline_access',
              'https://outlook.office.com/user.read',
              'https://outlook.office.com/mail.read',
              'https://outlook.office.com/mail.send'
              ]

    # Client ID and secret
    @staticmethod
    def get_client_secrets_from_env():
        try:
            client_id = outlook_credentials['OutlookOAuthClientId']
            client_secret = outlook_credentials['OutlookOAuthClientSecret']
        except Exception as e:
            logger.error("Failed to get Outlook OAuth credentials. Exception: {}".format(e))
            return None, None
        return client_id, client_secret

    @staticmethod
    def exchange_code_for_credentials(auth_code):
        client_id, client_secret = OutlookAuthorizer.get_client_secrets_from_env()
        logger.info("client id {}, client secret {}".format(client_id, client_secret))
        if not client_id or not client_secret:
            return AuthVerifyResult(code=AuthVerifyResultCode.server_error,
                                    message='Outlook OAuth client credentials are not properly set. Please check your Lambda function environment variable or '
                                            'CloudFormation stack parameter')

        # Build the post form for the token request
        post_data = {'grant_type': 'authorization_code',
                     'code': auth_code,
                     'redirect_uri': OutlookAuthorizer.redirect_url,
                     'scope': ' '.join(str(i) for i in OutlookAuthorizer.scopes),
                     'client_id': client_id,
                     'client_secret': client_secret
                     }

        r = requests.post(OutlookAuthorizer.token_url, data=post_data)

        logger.info("Response for access token: {}".format(r))

        try:
            result_data = r.json()
        except Exception as e:
            return AuthVerifyResult(code=AuthVerifyResultCode.auth_code_invalid,
                                    message='Error retrieving token: {0} - {1}. Exception: {2}'.format(r.status_code,
                                                                                                       r.text, e))
        if 'error' in result_data and result_data['error']:
            return AuthVerifyResult(code=AuthVerifyResultCode.auth_code_invalid,
                                    message="Unable to retrieve token with the given auth code. Error from Outlook OAuth: {}".format(result_data['error_description']))

        credentials = OAuthCredentials(access_token=result_data['access_token'],
                                       refresh_token=result_data['refresh_token'],
                                       expires_in_seconds=result_data['expires_in'])
        return AuthVerifyResult(code=AuthVerifyResultCode.success,
                                message="Token retrieved successfully",
                                credentials=credentials)

    @staticmethod
    def refresh_token(refresh_token):
        client_id, client_secret = OutlookAuthorizer.get_client_secrets_from_env()
        logger.info("client id {}, client secret {}".format(client_id, client_secret))
        if not client_id or not client_secret:
            return AuthVerifyResult(code=yeti_models.AuthVerifyResultCode.server_error,
                                    message='Outlook OAuth client ID or client secret is not properly set')

        # Build the post form for the token request
        post_data = {'grant_type': 'refresh_token',
                     'refresh_token': refresh_token,
                     'redirect_uri': OutlookAuthorizer.redirect_url,
                     'scope': ' '.join(str(i) for i in OutlookAuthorizer.scopes),
                     'client_id': client_id,
                     'client_secret': client_secret
                     }

        r = requests.post(OutlookAuthorizer.token_url, data=post_data)

        try:
            result_data = r.json()
        except Exception as e:
            return AuthVerifyResult(code=yeti_models.AuthVerifyResultCode.auth_code_invalid,
                                    message='Error retrieving token: {0} - {1}. Exception: {2}'.format(r.status_code, r.text, e))
        if 'error' in result_data and result_data['error']:
            return AuthVerifyResult(code=yeti_models.AuthVerifyResultCode.auth_code_invalid,
                                    message="Unable to retrieve token with the given auth code. Error from Outlook OAuth: {}".format(result_data['error_description']))

        credentials = OAuthCredentials(access_token=result_data['access_token'],
                                       refresh_token=result_data['refresh_token'],
                                       expires_in_seconds=result_data['expires_in'])
        return AuthVerifyResult(code=yeti_models.AuthVerifyResultCode.success,
                                message="Token retrieved successfully",
                                credentials=credentials)


class LoginAuthorizer:
    @staticmethod
    def generate_jwt_token(login_email, secret):
        token = jwt.encode({'login_email': login_email}, secret)
        token_utf8 = token.decode('utf-8')
        return token_utf8

    @staticmethod
    def auth_non_login_event(event):
        try:
            authorization_header = event['headers']['Authorization']
        except (KeyError, TypeError):
            return yeti_api_response.client_error("Cannot read property 'Authorization' from request header"), None

        try:
            login_email = event['headers']['login-email']
        except (KeyError, TypeError):
            return yeti_api_response.client_error("Cannot read property 'login-email' or 'loginemail' from request header"), None

        authorization_components = authorization_header.split(" ")
        if len(authorization_components) == 0 or authorization_components[0] != 'Bearer':
            return yeti_api_response.client_error("Only 'Bearer' header type for Authorization is supported. Please set the Authorization header to 'Bearer <token>'"), None
        if len(authorization_components) < 2 or not authorization_components[1]:
            return yeti_api_response.client_error("Authorization token cannot be found"), None

        token = authorization_components[1]

        auth_verify_result = LoginAuthorizer.verify_jwt_token(login_email=login_email, token=token)

        if not auth_verify_result:
            return yeti_api_response.internal_error("An error occurred when verifying token. Failed to retrieve auth verification result"), None
        elif auth_verify_result.code != constants.AuthVerifyResultCode.success:
            return yeti_api_response.client_error("Permission Denied. Code: {}, Message: {}".format(auth_verify_result.code, auth_verify_result.message)), None

        return None, login_email

    @staticmethod
    def verify_jwt_token(token, login_email):
        if not token:
            return AuthVerifyResult(code=constants.AuthVerifyResultCode.token_missing, message="Token is not set")

        try:
            response = logins_table.get_item(
                Key={
                    'Email': login_email
                }
            )
        except ClientError as e:
            return AuthVerifyResult(code=constants.AuthVerifyResultCode.server_error,
                                    message="Cannot read data from logins table. Response: {}".format(e.response['Error']['Message']))
        else:
            if 'Item' not in response or not response['Item']:
                return AuthVerifyResult(code=constants.AuthVerifyResultCode.login_email_nonexistent, message="Login email not found")
            else:
                item = response['Item']
            if 'Secret' not in item or not item['Secret']:
                return AuthVerifyResult(code=constants.AuthVerifyResultCode.password_mismatch, message="No secret is found for the login email")
            secret = item['Secret']

            logger.info("Successfully put logins data with response: {}".format(response))

        try:
            token = token.strip()
            decoded_token = jwt.decode(token, secret)
            token_login_email = decoded_token['login_email']
            if not token_login_email or token_login_email != login_email:
                return AuthVerifyResult(code=constants.AuthVerifyResultCode.token_invalid, message="Token's login_email is empty or doesn't match header's login_email")
        except jwt.DecodeError:
            return AuthVerifyResult(code=constants.AuthVerifyResultCode.token_invalid, message="Token validation failed")
        return AuthVerifyResult(code=constants.AuthVerifyResultCode.success, message="Token validation succeeded")



