import logging
import json
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

import api_response as api_response
from dynamodb import transactions_table
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

def transform_emails(event, context):
    try:

        logger.info("Got a transform email request: {}".format(event))
        error_response, user_email = LoginAuthorizer.auth_non_login_event(event)
        if error_response is not None:
            return api_response.client_error("error during login", error_response)

        access_token = get_token_from_email(email)
        print access_token

        # Transform logic for login_email
        transform_emails_util(access_token, user_email)
    except Exception as e:
        return api_response.internal_error(e)

    return api_response.ok_no_data("success")

# method that takes access token and user email to transform new emails in given email account.
# Separated from transform_emails for easier local testing
def transform_emails_util(access_token, user_email):
    timestamp = get_latest_timestamp_from_table(user_email)
    # print timestamp

    response = outlook_service.get_messages_received_after(access_token, user_email, timestamp)
    if 'value' not in response:
        raise ValueError(response)
    new_emails = response['value']

    # start_time = time.time()
    timestamp = 0
    for email in new_emails:
        curr_time = transform_email_to_transaction(user_email, email)
        if curr_time > timestamp:
            timestamp = curr_time
    # end_time = time.time()
    # print end_time-start_time
    record_last_timestamp(user_email, timestamp)

# get timestamp of last processed transaction given email from ddb
def get_latest_timestamp_from_table(user_email):
    #TODO: Implement
    return "2014-09-01T00:00:00Z"

def record_last_timestamp(user_email, timestamp):
    #TODO: Implement
    return True

def transform_email_to_transaction(user_email_address, email):
    # print("email: {}".format(email))
    transaction = email_parser.parse(email['body']['content'])
    print("Transaction parsed: {} {}".format(transaction, not transaction))
    if not transaction: #if empty transaction, means it's not a transaction email TODO: needs better handling here
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

        email_timestamp = email['receivedDateTime'] # 'receivedDateTime': '2018-01-15T16:31:46Z'
        email_timestamp_unix = "%.15g" % time.mktime(datetime.datetime.strptime(email_timestamp, "%Y-%m-%dT%H:%M:%SZ").timetuple())
        #Convert normal 2018-01-15T16:31:46Z to unix
        # converts float to decimal
        print email_timestamp_unix


        direction = 1 if (transaction['operator'] == "+") else 0
        print direction

        transactions_table.put_item(Item={
            "TransactionId" : transaction['transaction_id'],
            "TransactionPlatform" : "venmo",
            "Amount" : transaction['amount'],
            "Comments" : "N/A",
            "FriendId" : friend_id,
            "FriendName" : friend_name,
            "SerializedUpdateHistory" : [],
            "StatusCode" : 0, # 0 for not confirmed, 1 for confirmed
            "TransactionUnixTimestamp" : email_timestamp_unix,
            "UserEmail" : user_email_address,
            "UserId" : user_id,
            "Direction" : direction # 0 if you pay someone, 1 if someone pays you.
        })
        return email_timestamp
