import datetime
import re
import traceback

import outlook_service
import aws_client_dynamodb
import yeti_api_response
import yeti_exceptions
import yeti_logging
import yeti_service_auth
import yeti_service_user
import yeti_utils_lambda_handler

logger = yeti_logging.get_logger("YetiUserApi")


def create_buyer_account(event, context):
    try:
        body = yeti_utils_lambda_handler.get_body(event)
        user_email = body['user_email']

        if not re.match(r"[^@]+@[^@]+\.[^@]+", user_email):
            raise yeti_exceptions.YetiApiBadEmailFormatException("{} is a bad email format".format(user_email))
        if user_email.split('@')[1] != 'amazon.com':
            raise yeti_exceptions.YetiApiIllegalEmailAddressException("{} is not an acceptable email address".format(user_email))

        verification_code = yeti_service_user.create_buyer_account(user_email)

        logger.info("New user created. Verification code: {}".format(verification_code))
        return yeti_api_response.ok_no_data()

    except yeti_exceptions.YetiApiClientErrorException as e:
        logger.info("Client error. Error trace: {}".format(traceback.format_exc()))
        return yeti_api_response.client_error(str(e))

    except (yeti_exceptions.YetiApiInternalErrorException, Exception) as e:
        logger.error(traceback.format_exc())
        return yeti_api_response.internal_error(str(e))


