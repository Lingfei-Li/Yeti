import decimal
import json

import html2text
import re
import logging
from bs4 import BeautifulSoup

import yeti_exceptions

logger = logging.getLogger("YetiCommonUtils")
logger.setLevel(logging.INFO)


def replace_decimals(obj):
    if isinstance(obj, list):
        for i in range(len(obj)):
            obj[i] = replace_decimals(obj[i])
        return obj
    elif isinstance(obj, dict):
        for key, val in obj.items():
            obj[key] = replace_decimals(val)
        return obj
    elif isinstance(obj, decimal.Decimal):
        if obj % 1 == 0:
            return int(obj)
        else:
            return float(obj)
    else:
        return obj

