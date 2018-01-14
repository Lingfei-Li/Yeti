from botocore.exceptions import ClientError
import logging
import jwt
import requests

from dynamodb import logins_table
import constants as constants
import utils

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class AuthVerifyResult:
    code = None
    message = None
    token = None
    data = None

    def __init__(self, code, message="", token=None, data=None):
        self.code = code
        self.message = message
        self.token = token
        self.data = data


class OutlookAuthorizer:
    # Constant strings for OAuth2 flow
    # The OAuth authority
    authority = 'https://login.microsoftonline.com'

    # The authorize URL that initiates the OAuth2 client credential flow for admin consent
    authorize_url = '{0}{1}'.format(authority, '/common/oauth2/v2.0/authorize?{0}')

    # The token issuing endpoint
    token_url = '{0}{1}'.format(authority, '/common/oauth2/v2.0/token')

    # The redirect url must align with the redirect url used for signin
    test_redirect_url = 'http://localhost:8000/tutorial/gettoken/'
    redirect_url = 'https://auth.expo.io/@drinkiit/yeti-mobile'

    # The scopes required by the app
    scopes = ['openid',
              'offline_access',
              'User.Read',
              'Mail.Read'
              ]

    # Client ID and secret
    @staticmethod
    def get_client_credentials():
        try:
            client_id = utils.decrypt_for_key('OutlookOAuthClientIdCipherText').decode('utf-8')
            client_secret = utils.decrypt_for_key('OutlookOAuthClientSecretCipherText').decode('utf-8')
        except Exception as e:
            logger.error("Failed to decode Outlook OAuth credentials. Exception: {}".format(e))
            return None, None
        return client_id, client_secret

    @staticmethod
    def outlook_oauth(auth_code):
        client_id, client_secret = OutlookAuthorizer.get_client_credentials()
        logger.info("client id {}, client secret {}".format(client_id, client_secret))
        if not client_id or not client_secret:
            return AuthVerifyResult(code=constants.AuthVerifyResultCode.server_error, message='Outlook OAuth client credentials are not properly set. Please check your Lambda '
                                                                                              'function environment variable or CloudFormation stack parameter')

        # Build the post form for the token request
        post_data = {'grant_type': 'authorization_code',
                     'code': auth_code,
                     'redirect_uri': OutlookAuthorizer.redirect_url,
                     'scope': ' '.join(str(i) for i in OutlookAuthorizer.scopes),
                     'client_id': client_id,
                     'client_secret': client_secret
                     }

        r = requests.post(OutlookAuthorizer.token_url, data=post_data)

        try:
            result_data = r.json()
        except Exception as e:
            return AuthVerifyResult(code=constants.AuthVerifyResultCode.auth_code_invalid, message='Error retrieving token: {0} - {1}. Exception: {2}'.format(r.status_code,
                                                                                                                                                              r.text, e))
        if 'error' in result_data and result_data['error']:
            return AuthVerifyResult(code=constants.AuthVerifyResultCode.auth_code_invalid, message="Unable to retrieve token with the given auth code. Error from Outlook OAuth: "
                                                                                                   "{}".format(result_data['error_description']))
        return AuthVerifyResult(code=constants.AuthVerifyResultCode.success, message="Token retrieved successfully", data=r.json())

    @staticmethod
    def refresh_token(refresh_token):
        client_id, client_secret = OutlookAuthorizer.get_client_credentials()
        logger.info("client id {}, client secret {}".format(client_id, client_secret))
        if not client_id or not client_secret:
            return AuthVerifyResult(code=constants.AuthVerifyResultCode.server_error, message='Outlook OAuth client credentials are not properly set')

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
            return AuthVerifyResult(code=constants.AuthVerifyResultCode.auth_code_invalid, message='Error retrieving token: {0} - {1}. Exception: {2}'.format(r.status_code,
                                                                                                                                                              r.text, e))

        if 'error' in result_data and result_data['error']:
            return AuthVerifyResult(code=constants.AuthVerifyResultCode.auth_code_invalid, message="Unable to retrieve token with the given auth code. Error from Outlook OAuth: "
                                                                                                   "{}".format(result_data['error_description']))
        return AuthVerifyResult(code=constants.AuthVerifyResultCode.success, message="Token refreshed successfully", data=r.json())


class LoginAuthorizer:
    @staticmethod
    def generate_jwt_token(login_email, secret):
        token = jwt.encode({'login_email': login_email}, secret)
        token_utf8 = token.decode('utf-8')
        return token_utf8

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
            data = jwt.decode(token, secret)
            token_login_email = data['login_email']
            if not token_login_email or token_login_email != login_email:
                return AuthVerifyResult(code=constants.AuthVerifyResultCode.token_invalid, message="Token's login_email is empty or doesn't match header's login_email", data=data)
        except jwt.DecodeError:
            return AuthVerifyResult(code=constants.AuthVerifyResultCode.token_invalid, message="Token validation failed")
        return AuthVerifyResult(code=constants.AuthVerifyResultCode.success, message="Token validation succeeded", data=data)
