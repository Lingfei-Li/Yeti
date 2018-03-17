import datetime
import traceback

import outlook_service
import aws_client_dynamodb
import yeti_api_response
import yeti_exceptions
import yeti_logging
import yeti_service_auth
import yeti_utils_lambda_handler
from yeti_utils_auth import LoginAuthorizer

logger = yeti_logging.get_logger("YetiAuthApi")


def renew_outlook_notification_subscription(event, context):

    logger.info("Start")

    try:
        emails = event['emails']
    except Exception as e:
        logger.error("Failed to get emails from scheduled job input. Error: {}".format(e))
        return

    # Get the subscription id for the email address in the request
    for email in emails:
        logger.info("Checking outlook notification subscription for ".format(email))
        try:
            access_token = yeti_service_auth.get_access_token_for_email(email)
            logger.info("Current access token: {}".format(access_token))
            subscription_id, subscription_expiry_datetime = yeti_service_auth.get_outlook_notification_subscription_for_email(email)
            if subscription_id is None or subscription_expiry_datetime is None:
                logger.info('There is no subscription associated with the email. Creating a new subscription for {}'.format(email))
                subscription_id, subscription_expiry_datetime = outlook_service.create_notification_subscription(access_token, email)
                logger.info('Successfully created a new subscription')
            elif subscription_expiry_datetime < datetime.datetime.now(subscription_expiry_datetime.tzinfo) - datetime.timedelta(days=1):
                logger.info('Current subscription: ID: {}, Expiration: {}'.format(subscription_id, subscription_expiry_datetime.isoformat()))
                logger.info('Subscription will expire in 1 day or has expired')
                try:
                    logger.info('Trying to renew subscription for {}'.format(email))
                    subscription_id, subscription_expiry_datetime = outlook_service.renew_subscription(access_token, email, subscription_id)
                    logger.info('Successfully renewed the new subscription')
                except yeti_exceptions.OutlookApiErrorException:
                    logger.info('Failed to renew subscription. Trying to create a new one for {}'.format(email))
                    subscription_id, subscription_expiry_datetime = outlook_service.create_notification_subscription(access_token, email)
                    logger.info('Successfully created a new subscription')
            else:
                logger.info('The current subscription is valid')
                continue

            # Update the subscription in DB
            aws_client_dynamodb.AuthServiceAuthTable.update_auth_item_outlook_notification_subscription(email, subscription_id, subscription_expiry_datetime)
            logger.info('Updated subscription inserted to db: ID: {}, Expiration: {}'.format(subscription_id, subscription_expiry_datetime.isoformat()))

        except Exception as e:
            logger.error(traceback.format_exc())
            logger.error("Failed to renew/create outlook notification subscription for {}".format(email))
            raise e
    logger.info("Subscriptions for all emails checked.")


def outlook_oauth(event, context):
    try:
        body = yeti_utils_lambda_handler.get_body(event)
        auth_code = body['auth_code']

        # Delegate to the auth service for oauth login. Retrieve the auth_item (yeti_models.Auth) with necessary information
        auth_item = yeti_service_auth.oauth_login(auth_code)

        # Create a jwt and return it to front end
        response = {
            'message': 'Outlook OAuth success',
            'loginEmail': auth_item.email,
            'token': LoginAuthorizer.generate_jwt_token(login_email=auth_item.email, secret=auth_item.secret)
        }

        logger.info("Sending response: {}".format(response))
        return yeti_api_response.ok(response)

    except yeti_exceptions.YetiApiClientErrorException as e:
        logger.info("Client error. Error trace: {}".format(traceback.format_exc()))
        return yeti_api_response.client_error(str(e))

    except (yeti_exceptions.YetiApiInternalErrorException, Exception) as e:
        logger.error(traceback.format_exc())
        return yeti_api_response.internal_error(str(e))





