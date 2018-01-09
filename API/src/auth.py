from botocore.exceptions import ClientError
import logging
import jwt
import requests

from dynamodb import logins_table
import constants as constants
from constants import AuthVerifyResultCodes

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
    # Client ID and secret
    client_id = '1420c3c4-8202-411f-870d-64b6166fd980'
    client_secret = 'rFSZQ47995(}]hmfsbqXDL%'

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
              'Mail.Read',
              'Calendars.Read',
              'Contacts.Read']

    @staticmethod
    def outlook_oauth(auth_code):
        # Build the post form for the token request
        post_data = {'grant_type': 'authorization_code',
                     'code': auth_code,
                     'redirect_uri': OutlookAuthorizer.redirect_url,
                     'scope': ' '.join(str(i) for i in OutlookAuthorizer.scopes),
                     'client_id': OutlookAuthorizer.client_id,
                     'client_secret': OutlookAuthorizer.client_secret
                     }

        r = requests.post(OutlookAuthorizer.token_url, data=post_data)

        try:
            result_data = r.json()
        except Exception as e:
            return AuthVerifyResult(code=constants.AuthVerifyResultCodes.auth_code_invalid, message='Error retrieving token: {0} - {1}. Exception: {2}'.format(r.status_code,
                                                                                                                                                               r.text, e))
        if 'error' in result_data and result_data['error']:
            return AuthVerifyResult(code=constants.AuthVerifyResultCodes.auth_code_invalid, message="Unable to retrieve token with the given auth code. Error from Outlook OAuth: "
                                                                                                    "{}".format(result_data['error_description']))
        return AuthVerifyResult(code=constants.AuthVerifyResultCodes.success, message="Token retrieved successfully", data=r.json())


class LoginAuthorizer:
    @staticmethod
    def generate_jwt_token(login_email, secret):
        token = jwt.encode({'login_email': login_email}, secret)
        token_utf8 = token.decode('utf-8')
        return token_utf8

    @staticmethod
    def verify_jwt_token(token, login_email):
        try:
            response = logins_table.get_item(
                Key={
                    'Email': login_email
                }
            )
        except ClientError as e:
            return AuthVerifyResult(code=constants.AuthVerifyResultCodes.server_error, message="Cannot read data from logins table. Response: {}".format(e.response['Error']['Message']))
        else:
            if 'Item' not in response or not response['Item']:
                return AuthVerifyResult(code=constants.AuthVerifyResultCodes.login_email_nonexistent, message="Login email not found")
            else:
                item = response['Item']
            if 'Secret' not in item or not item['Secret']:
                return AuthVerifyResult(code=constants.AuthVerifyResultCodes.password_mismatch, message="No secret is specified for the login email")
            secret = item['Secret']

            logger.info("Successfully put logins data with response: {}".format(response))

        if not token:
            return AuthVerifyResult(code=constants.AuthVerifyResultCodes.token_missing, message="Token is not set")
        try:
            token = token.strip()
            data = jwt.decode(token, secret)
        except jwt.DecodeError:
            return AuthVerifyResult(code=constants.AuthVerifyResultCodes.token_invalid, message="Token validation failed")
        return AuthVerifyResult(code=constants.AuthVerifyResultCodes.success, message="Token validation succeeded", data=data)

