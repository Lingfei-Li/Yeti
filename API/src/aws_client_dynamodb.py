import boto3
import logging

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
    def get_payment_item(cls, payment_id, payment_method):
        key = {
            'payment_id': payment_id,
            'payment_method': payment_method
        }
        item = DynamoDBTable.get_item(table_name=cls.table_name, key=key, model_cls=yeti_models.Payment)
        return item


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
class OrderServiceTicketTable:
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
    def put_order_item(cls, order_item):
        dynamodb_item = order_item.to_dynamodb_item()
        DynamoDBTable.put_item(table_name=cls.table_name, item=dynamodb_item)


class OrderServicePaymentLocalView(PaymentServicePaymentTable):
    table_name = 'Yeti-OrderService-PaymentLocalView'


class OrderServiceTicketLocalView(TicketServiceTicketTable):
    table_name = 'Yeti-OrderService-TicketLocalView'


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

















