import logging

from decimal import Decimal

import dateutil.parser
import yeti_exceptions
import yeti_utils_email
from yeti_models import Payment

logger = logging.getLogger("YetiEmailService")
logger.setLevel(logging.INFO)

############################
# Constants
############################
YOU = "You "
ISO8601_FORMAT_TEMPLATE = "%Y-%m-%dT%H:%M:%SZ"


def extract_payment_from_email(email):
    """
    Extract the payment data from the email

    :param email: the email (JSON object) to be transformed
    :return: the extracted Payment data
    """

    logger.info("Extract payment from email")
    payment = yeti_utils_email.parse(email['Body']['Content'])

    logger.info("Payment parsed: {}".format(payment))

    if payment['operator'] != "+":
        raise yeti_exceptions.YetiInvalidPaymentEmailException()

    if payment['venmo_name_1'] == YOU:
        user_id = payment['venmo_id_1']
        payer_id = payment['venmo_id_2']
    else:
        user_id = payment['venmo_id_2']
        payer_id = payment['venmo_id_1']

    if user_id != 'AmazonSkiTickets3':
        logger.warning("Recipient ID {} is not AmazonSkiTickets3. This payment might be ignored".format(user_id))
        # TODO: raise yeti_exceptions.YetiInvalidPaymentEmailException() when in production

    payment_id = payment['payment_id']
    payment_method = 'venmo'
    amount = payment['amount']
    comments = payment['comments']
    email_received_datetime = email['ReceivedDateTime']  # 'ReceivedDateTime': '2018-01-15T16:31:46Z'

    payment_item = Payment.build(payment_id=payment_id,
                                 payment_method=payment_method,
                                 payer_id=payer_id,
                                 payment_amount=Decimal(str(amount)),
                                 payment_datetime=dateutil.parser.parse(email_received_datetime),
                                 order_id=comments,
                                 comments=[comments])
    return payment_item


