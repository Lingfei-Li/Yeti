import datetime
import json
import hashlib
import dateutil.parser
import re
import uuid
from decimal import Decimal
import copy

import yeti_exceptions
import yeti_utils_common


##############################################
# Common Models
##############################################


class YetiModel:
    def __init__(self):
        # Empty constructor used by DynamoDB mapper
        pass

    def to_json_obj(self):
        json_obj = copy.deepcopy(self.__dict__)
        for key, val in json_obj.items():
            if isinstance(val, datetime.datetime):
                json_obj[key] = val.isoformat()
        return yeti_utils_common.replace_decimals(json_obj)

    def to_json(self):
        return json.dumps(self.to_json_obj())

    def to_dynamodb_item(self):
        dynamodb_item = copy.deepcopy(self.__dict__)
        for key, val in dynamodb_item.items():
            if isinstance(val, datetime.datetime):
                dynamodb_item[key] = val.isoformat()
        return dynamodb_item

    @classmethod
    def from_dynamodb_item(cls, ddb_item):
        class_item = cls()
        for key, val in cls.__dict__.items():
            if not re.match(r"__.*__", key):
                if key in ddb_item:
                    if key.endswith('_datetime'):
                        class_item.__dict__[key] = dateutil.parser.parse(ddb_item[key])
                    else:
                        class_item.__dict__[key] = ddb_item[key]
        return class_item


class ChangeSet(YetiModel):
    operator_id = None
    change_datetime = None
    changed_properties = None
    notes = None

    @classmethod
    def build(cls, operator_id, change_datetime, changed_properties, notes=None):
        obj = cls()
        obj.operator_id = operator_id
        obj.change_datetime = change_datetime
        obj.changed_properties = changed_properties
        obj.notes = notes
        return obj

    # override YetiMode.to_json()
    def to_json(self):
        changed_properties_json = []
        for change in self.changed_properties:
            changed_properties_json.append(change.to_json())
        return json.dumps({
            'operator': self.operator_id,
            'change_datetime': self.change_datetime,
            'changed_properties': changed_properties_json
        })

    @staticmethod
    def from_sns_message(message):
        if message is None or 'changed_properties' not in message or message['changed_properties'] is None:
            return None
        changed_properties = []
        for c in message['changed_properties']:
            changed_properties.append(PropertyChange.from_sns_message(c))
        return ChangeSet.build(operator_id=message['operator_id'],
                               change_datetime=dateutil.parser.parse(message['change_datetime']),
                               changed_properties=changed_properties,
                               notes=message['notes']
                               )


class PropertyChange(YetiModel):
    property_name = None
    prev_val = None
    curr_val = None
    notes = None

    @classmethod
    def build(cls, property_name, prev_val, curr_val, notes=None):
        obj = cls()
        obj.property_name = property_name
        obj.prev_val = prev_val
        obj.curr_val = curr_val
        obj.notes = notes
        return obj

    @staticmethod
    def from_sns_message(message):
        if message is None:
            return None
        return PropertyChange.build(property_name=message['property_name'],
                                    prev_val=message['prev_val'],
                                    curr_val=message['curr_val'],
                                    notes=message['notes'],
                                    )


##############################################
# Payment Service Models
##############################################
class Payment(YetiModel):
    payment_id = None
    venmo_story_id = None
    payer_id = None
    payment_amount = None
    payment_datetime = None
    applied_order_id = None
    comments = None

    @classmethod
    def build(cls, payment_id, venmo_story_id, payer_id, payment_amount, payment_datetime, comments, applied_order_id=None):
        obj = cls()
        obj.payment_id = payment_id
        obj.venmo_story_id = venmo_story_id
        obj.payer_id = payer_id
        obj.payment_amount = Decimal(payment_amount)   # string
        obj.payment_datetime = payment_datetime
        obj.comments = comments
        obj.applied_order_id = applied_order_id  # used only in OrderService payment local view. left None in PaymentTable
        return obj

    @staticmethod
    def from_sns_message(message):
        try:
            return Payment.build(payment_id=message['payment_id'],
                                 venmo_story_id=message['venmo_story_id'],
                                 payer_id=message['payer_id'],
                                 payment_amount=Decimal(str(message['payment_amount'])),
                                 payment_datetime=dateutil.parser.parse(message['payment_datetime']),
                                 comments=message['comments'])
        except Exception as e:
            raise yeti_exceptions.YetiApiBadEventBodyException(e)


class PaymentSNSMessageRecordType(YetiModel):
    new_payment = 0
    order_id_update = 1


class PaymentSNSMessageRecord(YetiModel):
    notification_type = None
    serialized_data = None
    order_id = None

    @classmethod
    def build(cls, notification_type, serialized_data, order_id):
        obj = cls()
        obj.notification_type = notification_type
        obj.serialized_data = serialized_data
        obj.order_id = order_id
        return obj


class MessageNotificationStreamRecord(YetiModel):
    change_type = None
    source = None
    message_id = None
    user_email = None
    meta_data = None
    change_type_created = "Created"
    change_type_missed = "Missed"
    source_outlook = "outlook"

    @classmethod
    def build(cls, change_type, source, user_email, message_id=None, meta_data=None):
        obj = cls()
        obj.change_type = change_type
        obj.source = source
        obj.message_id = message_id
        obj.user_email = user_email
        obj.meta_data = meta_data
        return obj


##############################################
# Ticket Service Models
##############################################
class Ticket(YetiModel):
    ticket_id = None
    ticket_version = None
    ticket_amount = None
    ticket_type = None
    distributor_id = None
    distribution_location = None
    distribution_start_datetime = None
    distribution_end_datetime = None
    walk_in_start_datetime = None
    walk_in_end_datetime = None
    change_set = None
    status_code = None

    @classmethod
    def build(cls, ticket_amount, ticket_type, distributor_id, distribution_location, distribution_start_datetime, distribution_end_datetime, walk_in_start_datetime,
              walk_in_end_datetime, ticket_id=None, ticket_version=None, change_set=None, status_code=None):
        obj = cls()
        obj.ticket_amount = Decimal(ticket_amount)
        obj.ticket_type = ticket_type
        obj.distributor_id = distributor_id
        obj.distribution_location = distribution_location
        obj.distribution_start_datetime = distribution_start_datetime
        obj.distribution_end_datetime = distribution_end_datetime
        obj.walk_in_start_datetime = walk_in_start_datetime
        obj.walk_in_end_datetime = walk_in_end_datetime
        obj.change_set = change_set
        obj.status_code = TicketStatusCode.created if status_code is None else Decimal(status_code)

        # Compute the ticket_id with the ticket details fields
        obj.ticket_id = hashlib.md5(obj.to_json().encode('utf-8')).hexdigest() if ticket_id is None else ticket_id
        obj.ticket_version = Decimal(1) if ticket_version is None else Decimal(ticket_version)
        return obj

    @staticmethod
    def from_sns_message(message):
        try:
            return Ticket.build(ticket_id=message['ticket_id'],
                                ticket_version=Decimal(str(message['ticket_version'])),
                                ticket_amount=Decimal(str(message['ticket_amount'])),
                                ticket_type=message['ticket_type'],
                                distributor_id=message['distributor_id'],
                                distribution_location=message['distribution_location'],
                                distribution_start_datetime=dateutil.parser.parse(message['distribution_start_datetime']),
                                distribution_end_datetime=dateutil.parser.parse(message['distribution_end_datetime']),
                                walk_in_start_datetime=dateutil.parser.parse(message['walk_in_start_datetime']),
                                walk_in_end_datetime=dateutil.parser.parse(message['walk_in_end_datetime']),
                                change_set=ChangeSet.from_sns_message(message['change_set']),
                                status_code=Decimal(str(message['status_code']))
                                )
        except Exception as e:
            raise yeti_exceptions.YetiApiBadEventBodyException(e)


class TicketStatusCode:
    created = 0
    cancelled = 1


##############################################
# Order Service Models
##############################################
class Order(YetiModel):
    order_id = None
    order_version = None
    ticket_id = None
    ticket_version = None
    buyer_id = None
    purchase_amount = None
    order_datetime = None
    expiry_datetime = None
    payment_id_list = None
    change_set = None
    status_code = None

    @classmethod
    def build(cls, ticket_id, ticket_version, buyer_id, purchase_amount, order_datetime, expiry_datetime, order_id=None, order_version=None, payment_id_list=None, change_set=None, status_code=None):
        obj = cls()
        obj.ticket_id = ticket_id
        obj.ticket_version = ticket_version
        obj.buyer_id = buyer_id
        obj.purchase_amount = purchase_amount
        obj.order_datetime = order_datetime
        obj.expiry_datetime = expiry_datetime
        obj.payment_id_list = [] if payment_id_list is None else payment_id_list
        obj.change_set = change_set
        obj.status_code = OrderStatusCode.created if status_code is None else status_code

        # Compute the order_id with the order details fields
        obj.order_id = yeti_utils_common.generate_id_md5_digit_20_for_object(obj) if order_id is None else order_id
        obj.order_version = Decimal(1) if order_version is None else Decimal(order_version)
        return obj

    @classmethod
    def get_raw_hash(cls, order_item):
        """ Generate a hash for the order details (excluding order id and order version) """
        obj = copy.deepcopy(order_item)
        obj.order_id = None
        obj.order_version = None
        raw_order_id = yeti_utils_common.generate_id_md5_digit_20_for_object(obj)
        return raw_order_id


class OrderStatusCode:
    created = 0
    expired = 1
    completed = 2
    cancelled = 3
    refund_required = 4
    refund_completed = 5
    other = 6


##############################################
# Auth Service Models
##############################################
class Auth(YetiModel):
    email = None
    access_token = None
    refresh_token = None
    token_expiry_datetime = None
    auth_type = None
    secret = None
    status_code = None
    outlook_notification_subscription_id = None
    outlook_notification_subscription_expiry_datetime = None

    @classmethod
    def build(cls, email, access_token, refresh_token, token_expiry_datetime, auth_type, secret=None, status_code=None, outlook_notification_subscription_id=None,
              outlook_notification_subscription_expiry_datetime=None):
        obj = cls()
        obj.email = email
        obj.access_token = access_token
        obj.refresh_token = refresh_token
        obj.token_expiry_datetime = token_expiry_datetime
        obj.auth_type = auth_type
        obj.secret = str(uuid.uuid4()) if secret is None else secret
        obj.status_code = OrderStatusCode.created if status_code is None else status_code
        obj.outlook_notification_subscription_id = outlook_notification_subscription_id
        obj.outlook_notification_subscription_expiry_datetime = outlook_notification_subscription_expiry_datetime
        return obj


class OAuthCredentials:
    access_token = None
    refresh_token = None
    expiry_datetime = None

    def __init__(self, access_token, refresh_token=None, expires_in_seconds=None, expiry_datetime=None):
        self.access_token = access_token
        self.refresh_token = refresh_token
        if not expiry_datetime:
            self.expiry_datetime = datetime.datetime.now() + datetime.timedelta(seconds=expires_in_seconds - 300)
        elif not expires_in_seconds:
            self.expiry_datetime = expiry_datetime
        else:
            raise Exception("One of expires_in and expiration_datetime must be provided")


class AuthVerifyResult:
    code = None
    message = None
    credentials = None  # yeti_models.OAuthCredentials

    def __init__(self, code, message="", token=None, credentials=None):
        self.code = code
        self.message = message
        self.token = token
        self.credentials = credentials


class AuthVerifyResultCode:
    success = 0
    password_mismatch = 1
    login_email_nonexistent = 2
    login_email_suspended = 3
    device_suspended = 4
    server_error = 5
    token_invalid = 6
    token_expired = 7
    token_missing = 8
    auth_code_invalid = 9













