import json

import html2text
import re
import logging
from bs4 import BeautifulSoup

import yeti_exceptions

logger = logging.getLogger("YetiLambdaHandlerUtils")
logger.setLevel(logging.INFO)


def get_body(event):
    try:
        return json.loads(event['body'])
    except Exception as e:
        raise yeti_exceptions.YetiApiBadEventBodyException(e)



