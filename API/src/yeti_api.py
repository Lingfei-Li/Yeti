import logging
import json
from boto3.dynamodb.conditions import Key

import src.api_response as api_response
from src.dynamodb import transactions_table
from src.utils import replace_decimals

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def load_transactions(event, context):
    logger.info(event)

    if 'headers' not in event or event['headers'] is None or 'loginEmail' not in event['headers'] or not event['headers']['loginEmail']:
        return api_response.client_error({
            'error': "No 'loginEmail' set in request headers"
        })
    login_email = event['headers']['loginEmail']

    # Only return transactions sent to the login user
    filter_expression = Key('ReceiverEmail').eq(login_email)

    # Apply additional constraints
    if 'queryStringParameters' in event and event['queryStringParameters']:
        query = event['queryStringParameters']
        if 'Status' in query and query['Status']:
            filter_expression &= Key('Status').eq(query['Status'])
        if 'TransactionType' in query and query['TransactionType']:
            filter_expression &= Key('TransactionType').eq(query['TransactionType'])
        if 'PaymentMethod' in query and query['PaymentMethod']:
            filter_expression &= Key('PaymentMethod').eq(query['PaymentMethod'])

    response = transactions_table.scan(
        ProjectionExpression="SenderFirstName, SenderLastName, SenderEmail, Amount, TransactionUnixTimestamp, "
                             "#_Status, TransactionType",
        ExpressionAttributeNames={"#_Status": "Status"},
        FilterExpression=filter_expression
    )

    data = []
    for item in response['Items']:
        item = replace_decimals(item)
        data.append(item)

    return api_response.ok({
        'count': response['Count'],
        'data': data
    })


def search_transaction(event, context):
    logger.info(event)
    return api_response.ok({
        'message': "load transaction by id",
        'event': json.dumps(event)
    })


def close_transaction(event, context):
    logger.info(event)
    return api_response.ok({
        'message': "search transaction",
        'event': json.dumps(event)
    })

