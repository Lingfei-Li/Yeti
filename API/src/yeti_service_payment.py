import yeti_logging
from aws_client_kinesis import PaymentServiceMessageNotificationStream

logger = yeti_logging.get_logger("YetiPaymentService")


def publish_message_notifications_to_stream(message_notification_stream_records):
    logger.info("Putting {} message IDs to Kinesis stream".format(len(message_notification_stream_records)))
    records = []
    for record in message_notification_stream_records:
        records.append({
            'Data': record.to_json(),
            'PartitionKey': record.message_id
        })
        logger.info('Putting record: {}'.format(record.to_json()))

    # Publish to Kinesis in batches
    batch_size = 10
    start_pos = 0
    while start_pos < len(records):
        end_pos = min(start_pos + batch_size, len(records))
        PaymentServiceMessageNotificationStream.publish_message_notifications(records[start_pos:end_pos])
        start_pos += batch_size
