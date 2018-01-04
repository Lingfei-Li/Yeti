from botocore.exceptions import ClientError

import constants as constants
import jwt as jwt
from dynamodb import logins_table
from constants import AuthVerifyResultCodes
import requests


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


secret = 'secret'


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
                     'redirect_uri': 'http://localhost:8000/tutorial/gettoken/',
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

    @staticmethod
    def get_user_from_access_token(access_token):
        get_me_url = graph_endpoint.format('/me')

        # Use OData query parameters to control the results
        #  - Only return the displayName and mail fields
        query_parameters = {'$select': 'displayName,mail'}

        r = make_api_call('GET', get_me_url, access_token, "", parameters = query_parameters)

        if (r.status_code == requests.codes.ok):
            return r.json()
        else:
            return "{0}: {1}".format(r.status_code, r.text)
            pass


class Authorizer:
    @staticmethod
    def outlook_oauth(auth_code):
        pass

    @staticmethod
    def outlook_oauth(auth_code):
        pass

    @staticmethod
    def verify_email_password(login_email, password_hash):
        try:
            response = logins_table.get_item(
                Key={
                    "Email": login_email
                }
            )
        except ClientError as e:
            return AuthVerifyResult(code=AuthVerifyResultCodes.server_error, message=e.response['Error']['Message'])
        else:
            if 'Item' not in response:
                return AuthVerifyResult(code=AuthVerifyResultCodes.login_email_nonexistent, message="Email doesn't exist")
            item = response['Item']
            db_password_hash = item['PasswordHash']
            if password_hash!= db_password_hash:
                return AuthVerifyResult(code=AuthVerifyResultCodes.password_mismatch, message="Password doesn't match")
        # TODO: record login history
        # TODO: check device ID
        token = jwt.encode({'login_email': login_email, 'someotherdata': 'nothingspecial'}, secret)
        token_utf8 = token.decode('utf-8')
        return AuthVerifyResult(code=constants.AuthVerifyResultCodes.success, message="Email-Password Authentication succeeded", token=token_utf8)

    @staticmethod
    def verify_token(token):
        if not token:
            return AuthVerifyResult(code=constants.AuthVerifyResultCodes.token_missing, message="Token is not set")
        try:
            token = token.strip()
            data = jwt.decode(token, secret)
        except jwt.DecodeError:
            return AuthVerifyResult(code=constants.AuthVerifyResultCodes.token_invalid, message="Token validation failed")
        return AuthVerifyResult(code=constants.AuthVerifyResultCodes.success, message="Token validation succeeded", data=data)

