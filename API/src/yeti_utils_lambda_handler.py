import json

import yeti_exceptions
import yeti_logging

logger = yeti_logging.get_logger("YetiLambdaHandlerUtils")


def get_body(event):
    try:
        return json.loads(event['body'])
    except Exception as e:
        raise yeti_exceptions.YetiApiBadEventBodyException(e)



