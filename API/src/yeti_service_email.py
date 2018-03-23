from decimal import Decimal

import aws_client_dynamodb
import dateutil.parser
import outlook_service

import yeti_exceptions
import yeti_logging
import yeti_service_auth
import yeti_utils_email
from yeti_models import Payment

logger = yeti_logging.get_logger("YetiEmailService")

############################
# Constants
############################
YOU = "You "
ISO8601_FORMAT_TEMPLATE = "%Y-%m-%dT%H:%M:%SZ"


def check_email_type(email):
    return yeti_utils_email.check_content_type(email_subject=email['Subject'])


def extract_order_id_from_email(email):
    logger.info("Extract order id from email")

    email_content_type = yeti_utils_email.check_content_type(email_subject=email['Subject'])
    if email_content_type != yeti_utils_email.EmailContentType.payment_comment:
        raise yeti_exceptions.EmailTransformationErrorException('The email content is not a comment on a venmo transaction')

    order_id, venmo_story_id = yeti_utils_email.parse_venmo_comment_email(email_body_html=email['Body']['Content'])

    if order_id is None:
        raise yeti_exceptions.YetiInvalidPaymentEmailException('No valid order id found in the email')

    payment_id = aws_client_dynamodb.PaymentServicePaymentTable.get_payment_id_for_venmo_story_id(venmo_story_id)

    return payment_id, order_id


def extract_payment_from_email(email):
    """
    Extract the payment data from the email

    :param email: the email (object) to be transformed
    :return: the extracted Payment data
    """

    logger.info("Extract payment from email")

    email_content_type = yeti_utils_email.check_content_type(email_subject=email['Subject'])
    if email_content_type != yeti_utils_email.EmailContentType.new_payment:
        raise yeti_exceptions.EmailTransformationErrorException('The email content is not a valid venmo payment')

    payment = yeti_utils_email.parse_venmo_payment_email(email_body_html=email['Body']['Content'])
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
    venmo_story_id = payment['venmo_story_id']
    amount = payment['amount']
    order_id = payment['order_id']
    comments = payment['comments']
    email_received_datetime = email['ReceivedDateTime']  # 'ReceivedDateTime': '2018-01-15T16:31:46Z'

    payment_item = Payment.build(payment_id=payment_id,
                                 venmo_story_id=venmo_story_id,
                                 payer_id=payer_id,
                                 payment_amount=Decimal(str(amount)),
                                 payment_datetime=dateutil.parser.parse(email_received_datetime),
                                 comments=[comments])
    return payment_item, order_id


def send_email_from_yeti(recipient_email, subject, body):
    yeti_messenger_email = 'yeti-dev@outlook.com'
    yeti_messenger_access_token = yeti_service_auth.get_access_token_for_email(yeti_messenger_email)
    outlook_service.send_message(access_token=yeti_messenger_access_token,
                                 user_email=yeti_messenger_email,
                                 recipient_email=recipient_email,
                                 message_subject=subject,
                                 message_body=body)



