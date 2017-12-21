import logging
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)

CORS_HEADERS = {
    "Access-Control-Allow-Headers": "Content-Type,Authorization,X-Amz-Date,X-Api-Key,X-Amz-Security-Token",
    "Access-Control-Allow-Methods": "DELETE,GET,HEAD,OPTIONS,PATCH,POST,PUT",
    "Access-Control-Allow-Origin": "*"
}


def load_all_transactions(event, context):
    logger.info(event)
    return {
        'statusCode': 200,
        'headers': CORS_HEADERS,
        'body': json.dumps({
            'message': "hello",
            'event': json.dumps(event)
        })
    }
