import base64
import json

import boto3
from cloudformation_config import config

kinesis_client = boto3.client('kinesis', region_name='us-west-2')


class KinesisStream:
    @staticmethod
    def publish_records(stream_name, records):
        kinesis_client.put_records(StreamName=stream_name, Records=records)


class PaymentServiceMessageNotificationStream:
    stream_name = 'Yeti-PaymentService-MessageNotificationStream'

    @staticmethod
    def publish_message_notifications(records):
        KinesisStream.publish_records(PaymentServiceMessageNotificationStream.stream_name, records)

    @staticmethod
    def decode_stream_record(record):
        return json.loads(base64.b64decode(record['kinesis']['data']).decode('utf-8'))

