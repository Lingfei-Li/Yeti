import base64
import json

import boto3
from cloudformation_config import config

sns_client = boto3.client('sns', region_name='us-west-2')


class SNSTopic:
    @staticmethod
    def publish_message(topic_arn, message):
        sns_client.publish(TopicArn=topic_arn, Message=message)


class PaymentServicePaymentNotificationTopic:
    topic_arn = 'arn:aws:sns:us-west-2:917309224575:Yeti-PaymentService-PaymentNotificationTopic'

    @staticmethod
    def publish_message(payment_notification_message):
        SNSTopic.publish_message(PaymentServicePaymentNotificationTopic.topic_arn, payment_notification_message.to_json())


class TicketServiceTicketNotificationTopic:
    topic_arn = 'arn:aws:sns:us-west-2:917309224575:Yeti-TicketService-TicketNotificationTopic'

    @staticmethod
    def publish_message(ticket_notification_message):
        SNSTopic.publish_message(TicketServiceTicketNotificationTopic.topic_arn, ticket_notification_message.to_json())
