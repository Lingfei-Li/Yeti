import html2text
import re

import yeti_logging
from bs4 import BeautifulSoup

import yeti_exceptions

logger = yeti_logging.get_logger("YetiEmailUtils")

# Venmo Naming Conventions:
# First/Last Name - Letters Only
# Username - letters, numbers, (-), 5-16 in length
# payment ID seems to be 19 in length - Need to verify


# parses email in html format and returns a hash of key/value pairs derived from the email
def parse(email_html):
    payment = dict()

    h = html2text.HTML2Text()
    h.ignore_links = False
    h.body_width = 300
    email_md = h.handle(email_html)

    try:
        # gather my_venmo_id, payer_venmo_id, payer_name, amount
        payment.update(parse_payer_information(email_md))

        # payment_id
        payment.update(parse_payment_id(email_md))

        # time, amount(string type)
        payment.update(parse_time_amount_information(email_md))

        # comments
        payment.update(parse_comments(email_html))

        # thumbnail
        payment.update(parse_thumbnail(email_html))
    except Exception as e:
        raise yeti_exceptions.EmailTransformationErrorException(e)

    return payment


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


def append_key_value(keys, values):
    return dict((keys[i], values.group(i+1)) for i in range(0, len(keys)))
