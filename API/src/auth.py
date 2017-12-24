from botocore.exceptions import ClientError

import src.constants as constants
import src.lib.jwt as jwt
from src.dynamodb import logins_table
from src.constants import AuthVerifyResultCodes


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


class Authorizer:

    @staticmethod
    def verify_email_password(login_email, password_sha256):
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
            db_password_sha256 = item['PasswordSHA256']
            if password_sha256 != db_password_sha256:
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
