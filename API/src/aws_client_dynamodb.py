import json

import boto3
import logging

from boto3.dynamodb.conditions import Key

import yeti_exceptions
import yeti_logging
import yeti_models

dynamodb = boto3.resource('dynamodb', region_name='us-west-2')

##############################################
# v2.0 DynamoDB clients
##############################################
logger = yeti_logging.get_logger("YetiDynamoDB")


class DynamoDBTable:
    @staticmethod
    def put_item(table_name, item):
        try:
            table = dynamodb.Table(table_name)
            table.put_item(Item=item)
        except Exception as e:
            raise yeti_exceptions.DatabaseAccessErrorException("Failed to put item {} in database {}. Error: {}".format(item, table_name, e))

    @staticmethod
    def is_exist(table_name, key):
        """
        :return: True if the key exists in the table
        """
        try:
            table = dynamodb.Table(table_name)
            table.get_item(Key=key)
        except yeti_exceptions.DatabaseItemNotFoundError:
            return False
        except Exception as e:
            raise yeti_exceptions.DatabaseAccessErrorException("Failed to read database {} for key: {}. Error: {}".format(table_name, key, e))
        return True

    @staticmethod
    def get_item(table_name, key, model_cls):
        """ Get the item from DynamoDB and transform it into the provided model class
        :param table_name: the DDB table name
        :param key: the key map to get the DDB item
        :param model_cls: the destination model class to transform the DynamoDB item into
        :return: the model item (yeti_models.*). Transformation is done in yeti_models.YetiModel
        """
        try:
            table = dynamodb.Table(table_name)
            response = table.get_item(Key=key)
        except Exception as e:
            raise yeti_exceptions.DatabaseAccessErrorException("Failed to read database {} for key: {}. Error: {}".format(table_name, key, e))
        if 'Item' not in response or not response['Item']:
            raise yeti_exceptions.DatabaseItemNotFoundError("Required item (key: {}) for class {} does not exist in {}. ".format(key, model_cls, table_name))

        db_item = response['Item']

        class_item = model_cls.from_dynamodb_item(db_item)

        return class_item


##############################################
# Payment Service Databases
##############################################
class PaymentServicePaymentTable:
    table_name = 'Yeti-PaymentService-PaymentTable'

    @classmethod
    def put_payment_item(cls, payment_item):
        dynamodb_item = payment_item.to_dynamodb_item()
        DynamoDBTable.put_item(table_name=cls.table_name, item=dynamodb_item)

    @classmethod
    def get_payment_item(cls, payment_id):
        key = {
            'payment_id': payment_id
        }
        item = DynamoDBTable.get_item(table_name=cls.table_name, key=key, model_cls=yeti_models.Payment)
        return item

    @classmethod
    def update_order_id_for_payment_id(cls, payment_id, order_id):
        table = dynamodb.Table(cls.table_name)

        table.update_item(
            Key={
                'payment_id': payment_id
            },
            UpdateExpression="set order_id=:o",
            ExpressionAttributeValues={
                ':o': order_id
            }
        )

    @classmethod
    def get_payment_id_for_venmo_story_id(cls, venmo_story_id):
        table = dynamodb.Table(cls.table_name)

        response = table.query(
            IndexName='VenmoStoryIdIndex',
            KeyConditionExpression=Key('venmo_story_id').eq(venmo_story_id)
        )
        if response['Count'] != 1:
            raise yeti_exceptions.DatabaseItemNotExistentOrUniqueError('venmo_story_id should map to exactly one payment id, but found {} payments'.format(response['Count']))

        return response['Items'][0]['payment_id']


##############################################
# Ticket Service Databases
##############################################
class TicketServiceTicketTable:
    table_name = 'Yeti-TicketService-TicketTable'

    @classmethod
    def get_ticket_item(cls, ticket_id, ticket_version):
        key = {
            'ticket_id': ticket_id,
            'ticket_version': ticket_version
        }
        item = DynamoDBTable.get_item(table_name=cls.table_name, key=key, model_cls=yeti_models.Ticket)
        return item

    @classmethod
    def is_exist(cls, ticket):
        return DynamoDBTable.is_exist(table_name=cls.table_name, key={'ticket_id': ticket.ticket_id,
                                                                      'ticket_version': ticket.ticket_version})

    @classmethod
    def put_ticket_item(cls, ticket_item):
        dynamodb_item = ticket_item.to_dynamodb_item()
        DynamoDBTable.put_item(table_name=cls.table_name, item=dynamodb_item)


##############################################
# Order Service Databases
##############################################
class OrderServiceOrderTable:
    table_name = 'Yeti-OrderService-OrderTable'

    @classmethod
    def get_order_item(cls, order_id, order_version):
        key = {
            'order_id': order_id,
            'order_version': order_version
        }
        item = DynamoDBTable.get_item(table_name=cls.table_name, key=key, model_cls=yeti_models.Order)
        return item

    @classmethod
    def is_order_id_exist(cls, order_id):
        try:
            OrderServiceOrderTable.get_latest_order_item(order_id)
        except yeti_exceptions.DatabaseItemNotFoundError:
            return False
        return True

    @classmethod
    def get_latest_order_item(cls, order_id):
        table = dynamodb.Table(cls.table_name)

        response = table.query(
            KeyConditionExpression=Key('order_id').eq(order_id),
            Select='ALL_ATTRIBUTES',
            ScanIndexForward=False,
            Limit=1
        )
        if response['Count'] == 0:
            raise yeti_exceptions.DatabaseItemNotFoundError('Order id {} is not found in order service ticket local view.'.format(order_id))
        ddb_item = response['Items'][0]
        order = yeti_models.Order.from_dynamodb_item(ddb_item)
        return order

    @classmethod
    def put_order_item(cls, order_item):
        dynamodb_item = order_item.to_dynamodb_item()
        DynamoDBTable.put_item(table_name=cls.table_name, item=dynamodb_item)

    @classmethod
    def add_payment_id_for_order(cls, payment_id, order_id):
        order = cls.get_latest_order_item(order_id)
        order_version = order.order_version
        payment_id_list = order.payment_id_list
        if payment_id_list is None or not isinstance(payment_id_list, list):
            payment_id_list = []
        payment_id_list.append(payment_id)
        table = dynamodb.Table(cls.table_name)
        table.update_item(
            Key={
                'order_id': order_id,
                'order_version': order_version
            },
            UpdateExpression="set payment_id_list=:p",
            ExpressionAttributeValues={
                ':p': payment_id_list
            }
        )


class OrderServicePaymentLocalView(PaymentServicePaymentTable):
    table_name = 'Yeti-OrderService-PaymentLocalView'

    @classmethod
    def apply_order_id_to_payment(cls, payment_id, order_id):
        table = dynamodb.Table(cls.table_name)
        table.update_item(
            Key={
                'payment_id': payment_id
            },
            UpdateExpression="set applied_order_id=:a",
            ExpressionAttributeValues={
                ':a': order_id
            }
        )

    @classmethod
    def is_payment_id_attached_to_order(cls, payment_id):
        payment_item = cls.get_payment_item(payment_id)
        if payment_item.applied_order_id is None:
            return False
        return True


class OrderServiceTicketLocalView(TicketServiceTicketTable):
    table_name = 'Yeti-OrderService-TicketLocalView'

    @classmethod
    def get_latest_ticket_item(cls, ticket_id):
        table = dynamodb.Table(cls.table_name)

        response = table.query(
            KeyConditionExpression=Key('ticket_id').eq(ticket_id),
            Select='ALL_ATTRIBUTES',
            ScanIndexForward=False,
            Limit=1
        )
        if response['Count'] == 0:
            raise yeti_exceptions.DatabaseItemNotFoundError('Ticket id {} is not found in order service ticket local view.'.format(ticket_id))
        ddb_item = response['Items'][0]
        ticket = yeti_models.Ticket.from_dynamodb_item(ddb_item)
        return ticket


##############################################
# Auth Service Databases
##############################################
class AuthServiceAuthTable:
    table_name = 'Yeti-AuthService-AuthTable'

    @classmethod
    def get_auth_item(cls, email):
        key = {
            'email': email
        }
        item = DynamoDBTable.get_item(table_name=cls.table_name, key=key, model_cls=yeti_models.Auth)
        return item

    @classmethod
    def put_auth_item(cls, auth_item):
        dynamodb_item = auth_item.to_dynamodb_item()
        DynamoDBTable.put_item(table_name=cls.table_name, item=dynamodb_item)

    @classmethod
    def is_exist(cls, email):
        return DynamoDBTable.is_exist(table_name=cls.table_name, key={'email': email})

    @classmethod
    def update_auth_item_tokens(cls, email, access_token, refresh_token, token_expiry_datetime):
        """ Update the access token, the refresh token and expiry datetime for the email """

        table = dynamodb.Table(cls.table_name)
        table.update_item(
            Key={
                'email': email
            },
            UpdateExpression="set access_token=:a, refresh_token=:r, token_expiry_datetime=:t",
            ExpressionAttributeValues={
                ':a': access_token,
                ':r': refresh_token,
                ':t': token_expiry_datetime.isoformat()
            }
        )

    @classmethod
    def update_auth_item_outlook_notification_subscription(cls, email, subscription_id, subscription_expiry_datetime):
        """ Update the id and expiry for outlook notification subscription for the email """

        table = dynamodb.Table(cls.table_name)
        table.update_item(
            Key={
                'email': email
            },
            UpdateExpression="set outlook_notification_subscription_id=:i, outlook_notification_subscription_expiry_datetime=:e",
            ExpressionAttributeValues={
                ':i': subscription_id,
                ':e': subscription_expiry_datetime.isoformat()
            }
        )

















