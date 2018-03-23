import re
import datetime

import aws_client_dynamodb
import outlook_service
import yeti_logging
import yeti_models
import yeti_service_email
from yeti_models import AuthVerifyResultCode
import yeti_exceptions
from yeti_utils_auth import OutlookAuthorizer

logger = yeti_logging.get_logger("YetiUserService")


def create_buyer_account(user_email):
    """ Create a new user (buyer) and return the verification code. The new user will be pending verification"""
    existing_user = aws_client_dynamodb.UserServiceUserTable.get_nullable_user_item(user_email)
    if existing_user is None or existing_user.status_code != yeti_models.UserStatusCode.pending_verification:
        raise yeti_exceptions.YetiApiEmailAddressAlreadyExistsException("Cannot create new account. {} already exists.".format(user_email))

    new_user = yeti_models.User.build(email=user_email, user_type=yeti_models.UserType.buyer)
    aws_client_dynamodb.UserServiceUserTable.put_user_item(new_user)

    yeti_service_email.send_email_from_yeti(recipient_email=user_email,
                                            subject="[Yeti Ski Tickets] Verify your account",
                                            body="Verification code: {}".format(new_user.verification_code))
    return new_user.verification_code


