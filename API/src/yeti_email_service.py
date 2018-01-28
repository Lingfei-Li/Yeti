import logging
from botocore.exceptions import ClientError
from decimal import Decimal
import datetime
import time

import yeti_exceptions
from yeti_dynamodb import transactions_table, tokens_table
import outlook_service
import yeti_email_parser

logger = logging.getLogger("YetiEmailService")
logger.setLevel(logging.INFO)

############################
# Constants
############################
YOU = "You "
ISO8601_FORMAT_TEMPLATE = "%Y-%m-%dT%H:%M:%SZ"


def transform_emails_util(access_token, user_email):
    """
    Fetch all new emails since the last processed date, then transform the emails to transactions data.

    :param access_token: OAuth access token string
    :param user_email: the email address of the user
    """
    logger.info("Getting emails")

    last_processed_datetime = get_last_processed_datetime(user_email)
    if last_processed_datetime is None:
        new_emails = outlook_service.get_messages(access_token, user_email)
    else:
        last_processed_date_str_iso8601 = datetime.datetime.strftime(last_processed_datetime, ISO8601_FORMAT_TEMPLATE)
        new_emails = outlook_service.get_messages(access_token, user_email, last_processed_date_str_iso8601)

    last_processed_unix_timestamp = 0
    for email in new_emails:
        curr_unix_timestamp = transform_email_to_transaction(user_email, email)
        if curr_unix_timestamp > last_processed_unix_timestamp:
            last_processed_unix_timestamp = curr_unix_timestamp

    if last_processed_unix_timestamp != 0:
        put_last_processed_datetime(user_email, last_processed_unix_timestamp)


# get timestamp of last processed transaction given email from ddb
def get_last_processed_datetime(user_email):
    """
    Get the date (type: datetime) for the last processed email

    :param user_email: the email address of the user
    :return: the datetime of the last processed email
    """
    logger.info("get_last_processed_datetime")
    try:
        response = tokens_table.get_item(
            Key={
                'Email': user_email
            }
        )
    except ClientError as e:
        logger.error("Error getting last processed date from DynamoDB for email: {}. Error: {}".format(user_email, e.response['Error']['Message']))
        raise yeti_exceptions.DatabaseAccessErrorException("Error getting last processed date for email: {}. Error: {}".format(user_email, e.response['Error']['Message']))
    if 'Item' not in response or not response['Item']:
        logger.info("Email {} doesn't exist in DynamoDB".format(user_email))
        raise yeti_exceptions.DatabaseAccessErrorException("Email {} doesn't exist in DynamoDB".format(user_email))

    if 'LastProcessedUnixTimestamp' not in response['Item'] or response['Item']['LastProcessedUnixTimestamp'] is None:
        last_processed_unix_timestamp = 0
    else:
        last_processed_unix_timestamp = response['Item']['LastProcessedUnixTimestamp']

    return datetime.datetime.fromtimestamp(last_processed_unix_timestamp)


def put_last_processed_datetime(user_email, last_processed_unix_timestamp):
    logger.info("put_last_processed_datetime")
    tokens_table.update_item(
        Key={
            'Email': user_email
        },
        UpdateExpression="set LastProcessedUnixTimestamp=:l",
        ExpressionAttributeValues={
            ':l': Decimal(last_processed_unix_timestamp)
        }
    )


def transform_email_to_transaction(user_email_address, email):
    """
    Parse and transform the emails to transactions data model.

    :param user_email_address: the email address of the user
    :param email: the email (text) to be transformed
    :return: the receive time (unix timestamp) of the email
    """
    try:
        logger.info("Transform email to transaction")
        transaction = yeti_email_parser.parse(email['body']['content'])
        logger.info("Transaction parsed: {} {}".format(transaction, not transaction))
    except yeti_exceptions.EmailTransformationErrorException as e:
        logging.warning("Email failed to transform. Email object: {}. Error: {}".format(email, e))
        return 0

    logger.info("Transaction parsed: {}".format(transaction))

    if transaction['venmo_name_1'] == YOU:
        user_id = transaction['venmo_id_1']
        friend_name = transaction['venmo_name_2']
        friend_id = transaction['venmo_id_2']
    else:
        user_id = transaction['venmo_id_2']
        friend_name = transaction['venmo_name_1']
        friend_id = transaction['venmo_id_1']
    transaction_id = transaction['transaction_id']
    transaction_platform = 'venmo'
    amount = transaction['amount']
    thumbnail_uri = transaction['thumbnail_uri']
    comments = transaction['comments']

    email_received_date_str = email['receivedDateTime']  # 'receivedDateTime': '2018-01-15T16:31:46Z'
    email_unix_timestamp_decimal = "%.15g" % time.mktime(datetime.datetime.strptime(email_received_date_str, ISO8601_FORMAT_TEMPLATE).timetuple())
    # Convert normal 2018-01-15T16:31:46Z to unix
    # converts float to decimal

    direction = 1 if (transaction['operator'] == "+") else 0

    # Check transaction existence. Only update database if the transaction is not seen before
    response = transactions_table.get_item(Key={
                                         'TransactionId': transaction_id,
                                         'TransactionPlatform': transaction_platform
                                     })
    if 'Item' not in response or not response['Item']:
        transaction_item = {
            "TransactionId": transaction_id,
            "TransactionPlatform": transaction_platform,
            "Amount": amount,
            "Comments": comments,
            "ThumbnailURI": thumbnail_uri,
            "FriendId": friend_id,
            "FriendName": friend_name,
            "SerializedUpdateHistory": [],
            "StatusCode": 0,  # 0 for not confirmed, 1 for confirmed
            "TransactionUnixTimestamp": email_unix_timestamp_decimal,
            "UserEmail": user_email_address,
            "UserId": user_id,
            "Direction": direction  # 0 if you pay someone, 1 if someone pays you.
        }
        logger.info("Putting transaction item to table: \n{}".format(transaction_item))
        transactions_table.put_item(Item=transaction_item)
        return float(email_unix_timestamp_decimal)
    else:
        logger.info("Transaction [id: {}, platform: {}] is already in database, skipping...".format(transaction_id, transaction_platform))
        return 0


