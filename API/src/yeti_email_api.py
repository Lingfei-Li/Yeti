import logging
import json
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
import traceback

from decimal import Decimal

import api_response as api_response
from dynamodb import transactions_table, tokens_table
from auth import LoginAuthorizer
import outlook_service
import email_parser
import re
import datetime
import time

logger = logging.getLogger()
logger.setLevel(logging.INFO)

############################
# Constants
############################
YOU = "You "
ISO8601_FORMAT_TEMPLATE = "%Y-%m-%dT%H:%M:%SZ"


def transform_emails(event, context):
    try:
        logger.info("Got a transform email request: {}".format(event))
        error_response, login_email = LoginAuthorizer.auth_non_login_event(event)
        if error_response is not None:
            return error_response

        access_token = get_access_token_for_email(login_email)

        # Transform logic for login_email
        transform_emails_util(access_token, login_email)
    except Exception as e:
        print(traceback.format_exc())
        logger.error("Error transforming emails: {}".format(e))
        return api_response.internal_error("Error transforming emails: {}".format(e))

    return api_response.ok_no_data("success")


# method that takes access token and user email to transform new emails in given email account.
# Separated from transform_emails for easier local testing
def transform_emails_util(access_token, user_email):
    logger.info("transform_emails_util")

    last_processed_datetime = get_last_processed_datetime(user_email)
    if last_processed_datetime is None:
        response = outlook_service.get_messages(access_token, user_email)
    else:
        last_processed_date_str_iso8601 = datetime.datetime.strftime(last_processed_datetime, ISO8601_FORMAT_TEMPLATE)
        response = outlook_service.get_messages(access_token, user_email, last_processed_date_str_iso8601)

    if 'value' not in response:
        raise ValueError(response)

    new_emails = response['value']

    last_processed_unix_timestamp = 0
    for email in new_emails:
        curr_unix_timestamp = transform_email_to_transaction(user_email, email)
        if curr_unix_timestamp > last_processed_unix_timestamp:
            last_processed_unix_timestamp = curr_unix_timestamp

    if last_processed_unix_timestamp != 0:
        put_last_processed_datetime(user_email, last_processed_unix_timestamp)


# get timestamp of last processed transaction given email from ddb
def get_last_processed_datetime(user_email):
    logger.info("get_last_processed_datetime")
    # TODO: Fine-Tune error handling here
    try:
        response = tokens_table.get_item(
            Key={
                'Email': user_email
            }
        )
    except ClientError as e:
        logger.error("Error getting last processed date from DynamoDB for email: {}. Error: {}".format(user_email, e.response['Error']['Message']))
        return None
    if 'Item' not in response or not response['Item']:
        logger.info("Email {} doesn't exist in DynamoDB".format(user_email))
        raise Exception("Email {} doesn't have a last processed date.".format(user_email))
    if 'LastProcessedUnixTimestamp' not in response['Item'] or not response['Item']['LastProcessedUnixTimestamp']:
        logger.info("Email {} doesn't have a last processed date.".format(user_email))
        return None
    else:
        last_processed_unix_timestamp = response['Item']['LastProcessedUnixTimestamp']
        return datetime.datetime.fromtimestamp(last_processed_unix_timestamp)


def put_last_processed_datetime(user_email, last_processed_unix_timestamp):
    logger.info("put_last_processed_datetime")
    # TODO: Fine-Tune error handling here
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
    logger.info("transform_email_to_transaction")
    transaction = email_parser.parse(email['body']['content'])
    logger.info("Transaction parsed: {} {}".format(transaction, not transaction))
    if not transaction:  # if empty transaction, means it's not a transaction email TODO: needs better handling here
        return 0
    else:
        logger.info("Transaction parsed: {}".format(transaction))

        if transaction['venmo_name_1'] == YOU:
            user_id = transaction['venmo_id_1']
            friend_name = transaction['venmo_name_2']
            friend_id = transaction['venmo_id_2']
        else:
            user_id = transaction['venmo_id_2']
            friend_name = transaction['venmo_name_1']
            friend_id = transaction['venmo_id_1']

        email_received_date_str = email['receivedDateTime']  # 'receivedDateTime': '2018-01-15T16:31:46Z'
        email_unix_timestamp_decimal = "%.15g" % time.mktime(datetime.datetime.strptime(email_received_date_str, ISO8601_FORMAT_TEMPLATE).timetuple())
        # Convert normal 2018-01-15T16:31:46Z to unix
        # converts float to decimal
        logger.info(email_unix_timestamp_decimal)

        direction = 1 if (transaction['operator'] == "+") else 0
        logger.info(direction)

        transaction_item = {
            "TransactionId": transaction['transaction_id'],
            "TransactionPlatform": "venmo",
            "Amount": transaction['amount'],
            "Comments": "N/A",
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


def get_access_token_for_email(email):
    logger.info("get_token_for_email")
    # TODO: Fine-Tune error handling here
    try:
        response = tokens_table.get_item(Key={'Email': email})
    except ClientError as e:
        logger.error("Encountered ClientError while retrieving access token for email: {}. Error: {}".format(email, e.response['Error']['Message']))
        raise Exception("Encountered ClientError while retrieving access token for email: {}. Error: {}".format(email, e.response['Error']['Message']))
    if 'Item' not in response or not response['Item']:
        logger.info("Email {} doesn't exist in tokens table".format(email))
        raise Exception("Email {} doesn't exist in tokens table".format(email))
    if 'AccessToken' not in response['Item']:
        logger.info("AccessToken is missing for email {}".format(email))
        raise Exception("AccessToken is missing for email {}".format(email))
    return response['Item']['AccessToken']
