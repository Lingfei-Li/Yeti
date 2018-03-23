import datetime
import copy
import re

import aws_client_dynamodb
import outlook_service
import yeti_exceptions
import yeti_logging
import yeti_models
import yeti_service_auth
import yeti_service_email
import yeti_utils_common

logger = yeti_logging.get_logger("YetiOrderService")

ORDER_ID_MESSAGE_TEMPLATE = 'YetiOrder#{}#'
ORDER_ID_MESSAGE_REGEX_PATTERN = 'YetiOrder#([0-9]+)#'


def create_order(ticket_list, buyer_email):
    # Validate order
    for ticket in ticket_list:
        if 'ticket_id' not in ticket or 'ticket_version' not in ticket or 'ticket_type' not in ticket or 'distribution_location' not in ticket \
                or 'distribution_start_datetime' not in ticket or 'distribution_end_datetime' not in ticket or 'purchase_amount' not in ticket:
            raise yeti_exceptions.YetiApiClientErrorException("Missing required attributes in the ticketList for createOrder request")

        ordered_ticket = yeti_models.OrderedTicket.build(ticket_id=ticket['ticket_id'], ticket_version=ticket['ticket_version'], ticket_type=ticket['ticket_type'],
                                                         distribution_location=ticket['distribution_location'], distribution_start_datetime=ticket['distribution_start_datetime'],
                                                         distribution_end_datetime=ticket['distribution_end_datetime'], purchase_amount=ticket['purchase_amount'])

        ticket_id = ordered_ticket.ticket_id
        purchase_amount = ordered_ticket.purchase_amount

        # Availability Check
        total_ticket_amount = aws_client_dynamodb.OrderServiceTicketLocalView.get_total_ticket_amount(ticket_id)
        reserved_amount = get_reservation_amount(ticket_id)
        if purchase_amount + reserved_amount > total_ticket_amount:
            raise yeti_exceptions.YetiApiClientErrorException("Not enough tickets (id={}) available. Purchasing {}, {} reserved, {} total"
                                                              .format(ticket_id, purchase_amount, reserved_amount, total_ticket_amount))

    # We don't persist ordered tickets in DDB because Lingfei don't know how (and is reluctant to learn) to deserialize the DDB JSON into the correct data structure
    order = yeti_models.Order.build(ticket_list=ticket_list,
                                    buyer_email=buyer_email,
                                    order_datetime=datetime.datetime.now().isoformat(),
                                    expiry_datetime=datetime.datetime.now() + datetime.timedelta(minutes=10)
                                    )
    aws_client_dynamodb.OrderServiceOrderTable.put_order_item(order)
    logger.info("Order inserted to DB")
    return order.order_id


def get_orders_for_user_email(user_email):
    return aws_client_dynamodb.OrderServiceOrderTable.get_orders_for_user_email(user_email)


def handle_payment_notification(notification_type, data, order_id):
    if notification_type == yeti_models.PaymentSNSMessageRecordType.new_payment:
        logger.info('Payment notification: adding a new payment')
        payment = yeti_models.Payment.from_sns_message(data)
        aws_client_dynamodb.OrderServicePaymentLocalView.put_payment_item(payment)
        logger.info("Payment inserted to local view")
        if order_id is not None:
            logger.info("Payment has an order id: {}, updating order payment details".format(order_id))
            add_payment_id_for_order(payment.payment_id, order_id)

            __send_confirmation_email(order_id, payment.payment_id)
        else:
            logger.info("No order id is specified by the payment. Not attaching the payment to any order.")
    elif notification_type == yeti_models.PaymentSNSMessageRecordType.order_id_update:
        logger.info('Payment notification type: updating order ID for an existing payment')
        if order_id is not None:
            payment_id = data['payment_id']
            logger.info("Handling order id {} update for payment id: {}".format(order_id, payment_id))
            add_payment_id_for_order(payment_id, order_id)

            __send_confirmation_email(order_id, payment_id)
        else:
            logger.info("Order id is empty for the order id update message. Not attaching the payment to any order.")
    else:
        logger.info("Unknown notification type: {}".format(notification_type))


def __send_confirmation_email(order_id, payment_id):
    logger.info("Order updated with payment. Now sending confirmation email")
    buyer_email = aws_client_dynamodb.OrderServiceOrderTable.get_buyer_email_for_order(order_id)

    yeti_service_email.send_email_from_yeti(recipient_email=buyer_email,
                                                   subject="[Yeti Ski Tickets] Your payment is received",
                                                   body="Your Venmo payment (ID: {}) has been received for your order (ID: {}. BuyerId: {}).".format(payment_id, order_id,
                                                                                                                                                     buyer_email))


def add_payment_id_for_order(payment_id, order_id):
    # Check that the order id exists
    if not aws_client_dynamodb.OrderServiceOrderTable.is_order_id_exist(order_id):
        raise yeti_exceptions.DatabaseItemNotFoundError('Order id {} is not found'.format(order_id))

    # Check that the payment has not been applied to another order
    if aws_client_dynamodb.OrderServicePaymentLocalView.is_payment_id_attached_to_order(payment_id):
        raise yeti_exceptions.YetiPaymentAlreadyAppliedException('Payment {} is already applied to an order. Cannot change applied order or apply twice'.format(payment_id))

    logger.info("Adding the payment to order")
    aws_client_dynamodb.OrderServiceOrderTable.add_payment_id_for_order(payment_id, order_id)

    logger.info("Updating order service payment local view to apply order id to payment")
    aws_client_dynamodb.OrderServicePaymentLocalView.apply_order_id_to_payment(payment_id, order_id)


def get_reservation_amount(ticket_id):
    # TODO: get reservation amount
    # Reservation includes:
    # 1. paid orders (including picked, not-picked, completed)
    # 2. created not paid & not expired
    return 0


def generate_order_id_message(order_item):
    """ Generate a Venmo payment message that includes the order id """
    order_item_copy = copy.deepcopy(order_item)
    order_item_copy.order_id = None
    order_item_copy.order_version = None
    order_id = yeti_utils_common.generate_id_md5_digit_20_for_object(order_item_copy)
    return ORDER_ID_MESSAGE_TEMPLATE.format(order_id)


def validate_order_id_hash(order_item, order_id):
    raw_hash = yeti_models.Order.get_raw_hash(order_item)
    return raw_hash == order_id


def validate_order_id_message_format(order_id_message):
    if re.match(ORDER_ID_MESSAGE_REGEX_PATTERN, order_id_message):
        return True
    return False


