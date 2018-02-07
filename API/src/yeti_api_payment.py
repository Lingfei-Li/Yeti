import logging
import json
import traceback

import aws_client_sns
import outlook_service
import yeti_api_response as api_response
import aws_client_dynamodb
import yeti_exceptions
import yeti_service_email
from aws_client_kinesis import PaymentServiceMessageNotificationStream
from yeti_service_payment import publish_message_notifications_to_stream
from yeti_models import MessageNotificationStreamRecord
import yeti_service_auth

logger = logging.getLogger("YetiPaymentApi")
logger.setLevel(logging.INFO)


def handle_outlook_notification(event, context):
    """
    Lambda handler for Yeti-PaymentService-OutlookNotificationHandler
    """
    user_email = 'yeti-dev@outlook.com'
    logger.info("Received Outlook notification event: {}".format(event))
    try:
        validation_token = event['queryStringParameters']['validationtoken']
        return {
            'statusCode': 200,
            'headers': {
                "Access-Control-Allow-Headers": "Content-Type,Authorization,X-Amz-Date,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "DELETE,GET,HEAD,OPTIONS,PATCH,POST,PUT",
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "text/plain"
            },
            'body': validation_token
        }
    except Exception as e:
        logger.debug("Can't read validation token from outlook subscription request. error: {}".format(e))

    try:
        outlook_notifications = json.loads(event['body'])['value']
        message_notification_stream_records = []
        for n in outlook_notifications:
            change_type = n['ChangeType']
            if change_type == "Missed":
                record = MessageNotificationStreamRecord.build(change_type=MessageNotificationStreamRecord.change_type_missed,
                                                               source=MessageNotificationStreamRecord.source_outlook,
                                                               user_email=user_email,
                                                               message_id="NotApplicable")
                message_notification_stream_records.append(record)
            elif change_type == "Created":
                message_id = n['ResourceData']['Id']
                record = MessageNotificationStreamRecord.build(change_type=MessageNotificationStreamRecord.change_type_created,
                                                               source=MessageNotificationStreamRecord.source_outlook,
                                                               user_email=user_email,
                                                               message_id=message_id)
                message_notification_stream_records.append(record)

        publish_message_notifications_to_stream(message_notification_stream_records)
    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error("Failed to process outlook message notification. error: {}".format(e))

    return api_response.ok_no_data("")


def process_message_notification_stream(event, context):
    """
    Lambda handler for Yeti-PaymentService-MessageNotificationStreamProcessor
    """
    logger.info("Message notification stream event: {}".format(event))
    records = event['Records']

    for record in records:
        try:
            notification = PaymentServiceMessageNotificationStream.decode_stream_record(record)
            logger.info("notification: {}".format(notification))
        except Exception as e:
            logger.error("Failed to read Kinesis record. Error: {}".format(e))
            return

        try:
            change_type = notification['change_type']
            user_email = notification['user_email']
            if change_type == MessageNotificationStreamRecord.change_type_created:
                access_token = yeti_service_auth.get_access_token_for_email(user_email)
                email_object = outlook_service.get_message_for_id(notification['message_id'], access_token, user_email)
                logger.info("Message retrieved: {}".format(email_object))

                try:
                    payment_item = yeti_service_email.extract_payment_from_email(email_object)
                    logger.info("Payment extracted")
                except yeti_exceptions.YetiInvalidPaymentEmailException:
                    # Email is not relevant to payment. Ignoring.
                    continue

                aws_client_dynamodb.PaymentServicePaymentTable.put_payment_item(payment_item)
                logger.info("Payment inserted to db")

                # Notify other services about the payment via SNS
                payment_notification_message = payment_item  # Publish the entire payment object to SNS to create a local view in Order service
                aws_client_sns.PaymentServicePaymentNotificationTopic.publish_message(payment_notification_message)
                logger.info("Payment notification published to SNS")

            elif change_type == MessageNotificationStreamRecord.change_type_missed:
                logger.info("Change type == missed. Actively checking mailbox")
                # TODO: actively pull new emails and parse into payments

            else:
                logger.info("Unknown change type: {}".format(change_type))
                return
        except Exception as e:
            logger.error(traceback.format_exc())
            logger.error("Failed to process message notification. Error: {}".format(e))



