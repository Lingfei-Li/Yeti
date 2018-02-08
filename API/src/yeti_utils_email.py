import html2text
import re

import yeti_logging
import yeti_service_order
from bs4 import BeautifulSoup

import yeti_exceptions

logger = yeti_logging.get_logger("YetiEmailUtils")

# Venmo Naming Conventions:
# First/Last Name - Letters Only
# Username - letters, numbers, (-), 5-16 in length
# payment ID seems to be 19 in length - Need to verify


class EmailContentType:
    new_payment = 0
    payment_comment = 1
    venmo_transaction_history = 2
    others = 2


def check_content_type(email_subject):
    if 'paid' in email_subject and 'you' in email_subject:
        return EmailContentType.new_payment
    if 'commented on a payment between' in email_subject:
        return EmailContentType.payment_comment
    if 'Transaction History' in email_subject:
        return EmailContentType.venmo_transaction_history
    return EmailContentType.others


# parses email in html format and returns a hash of key/value pairs derived from the email
def parse_venmo_payment_email(email_body_html):
    payment = dict()

    h = html2text.HTML2Text()
    h.ignore_links = False
    h.body_width = 300
    email_body_md = h.handle(email_body_html)

    try:
        # gather my_venmo_id, payer_venmo_id, payer_name, amount
        payment.update(parse_payer_information(email_body_md))

        # payment_id
        payment.update(parse_payment_id(email_body_md))

        # time, amount(string type)
        payment.update(parse_time_amount_information(email_body_md))

        # story id (used for viewing the payment online)
        payment.update(parse_venmo_story_id(email_body_html))

        # order id
        payment.update(parse_order_id(email_body_md))

        # comments
        payment.update(parse_comments(email_body_html))

        # thumbnail
        payment.update(parse_thumbnail(email_body_html))
    except Exception as e:
        raise yeti_exceptions.EmailTransformationErrorException(e)

    return payment


def parse_venmo_comment_email(email_body_html):
    """ Parse the venmo comment notification email. Extract order id and venmo story id """
    payment = dict()

    h = html2text.HTML2Text()
    h.ignore_links = False
    h.body_width = 300
    email_body_md = h.handle(email_body_html)

    try:
        # story id (used for viewing the payment online)
        payment.update(parse_venmo_story_id(email_body_html))

        # order id
        payment.update(parse_order_id(email_body_md))
    except Exception as e:
        raise yeti_exceptions.EmailTransformationErrorException(e)

    return payment['order_id'], payment['venmo_story_id']


def parse_payer_information(email_md):
    name_id_matching_pattern = "\[([a-zA-Z\ ]+)\]\(https:\/\/venmo\.com\/([a-zA-Z\-0-9]{5,16})\)"
    action_matching_pattern = "(charged |paid )"
    name_id_regex = name_id_matching_pattern + action_matching_pattern + name_id_matching_pattern
    m = re.search(name_id_regex, email_md)

    # print m.groups()
    keys = ["venmo_name_1", "venmo_id_1", "action", "venmo_name_2", "venmo_id_2"]
    return append_key_value(keys, m)


def parse_time_amount_information(email_md):
    time_amount_regex = "!\[private\]\(https:\/\/s3\.amazonaws\.com\/venmo\/audience\/private\.png\) (\+|\\\-) \$([0-9]+\.[0-9]{2})"

    m = re.search(time_amount_regex, email_md)

    keys = ["operator", "amount"]
    return append_key_value(keys, m)


def parse_venmo_story_id(email_md):
    venmo_story_id_regex = "https:\/\/venmo\.com\/story\/([a-z0-9]+)[?\"/]"
    m = re.search(venmo_story_id_regex, email_md)

    keys = ["venmo_story_id"]
    return append_key_value(keys, m)


def parse_order_id(email_md):
    m = re.search(yeti_service_order.ORDER_ID_MESSAGE_REGEX_PATTERN, email_md)

    keys = ["order_id"]
    return append_key_value(keys, m, False)


def parse_comments(email_html):
    parsed_email_html = BeautifulSoup(email_html, 'html.parser')
    comments = parsed_email_html.find_all('p')[0].get_text()
    return {'comments': comments}


def parse_thumbnail(email_html):
    parsed_email_html = BeautifulSoup(email_html, 'html.parser')
    thumbnail_uri = parsed_email_html.find_all('a')[0].find('img').get('src')
    return {"thumbnail_uri": thumbnail_uri}


def parse_payment_id(email_md):
    payment_id_regex = "Payment ID: ([0-9]{19})"
    m = re.search(payment_id_regex, email_md)

    keys = ["payment_id"]
    return append_key_value(keys, m)


def append_key_value(keys, values, fail_on_error=True):
    d = dict()
    for i in range(0, len(keys)):
        try:
            d[keys[i]] = values.group(i+1)
        except Exception as e:
            if fail_on_error:
                raise e
            else:
                d[keys[i]] = None

    return d
