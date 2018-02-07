import datetime
import logging
import outlook_service
import yeti_service_auth
from yeti_auth_authorizers import LoginAuthorizer, OutlookAuthorizer
import yeti_email_parser
import time
from aws_client_dynamodb import transactions_table, logins_table, tokens_table
from bs4 import BeautifulSoup

from botocore.exceptions import ClientError
import yeti_email_service

FULL_FORMAT = '[%(levelname)s] %(asctime)s - %(name)s - %(message)s'
SHORT_FORMAT = '[%(levelname)s] %(message)s'
logging.basicConfig(format=SHORT_FORMAT, level=logging.INFO)
logger = logging.getLogger("EmailTransformationTest")


def update_user_transactions(user_email):
    access_token = yeti_service_auth.get_access_token_for_email(user_email)

    last_processed_datetime = yeti_email_service.get_last_processed_datetime(user_email)
    if last_processed_datetime is None:
        new_emails = outlook_service.get_messages(access_token, user_email)
    else:
        last_processed_date_str_iso8601 = datetime.datetime.strftime(last_processed_datetime, yeti_email_service.ISO8601_FORMAT_TEMPLATE)
        new_emails = outlook_service.get_messages(access_token, user_email, last_processed_date_str_iso8601)

    for email in new_emails:
        email_html = email['body']['content']
        parsed_email_html = BeautifulSoup(email_html, 'html.parser')
        # print(email_html)
        print(parsed_email_html.find_all('a')[0].find('img').get('src'))
        print(parsed_email_html.find_all('p')[0].get_text())
        # transform_email_to_transaction(email)


def transform_email_to_transaction(email):
    email_body = email['body']['content']
    logger.info("-----")
    yeti_email_parser.parse(email_body)
    logger.info("****")


update_user_transactions("yeti-dev@outlook.com")

