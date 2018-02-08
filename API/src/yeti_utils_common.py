import decimal
import hashlib

import yeti_logging

logger = yeti_logging.get_logger("YetiCommonUtils")


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


def generate_id_md5_digit_20_for_str(obj_str):
    return str(int(hashlib.md5(obj_str.encode('utf-8')).hexdigest(), 16) % 10**25)


def generate_id_md5_digit_20_for_object(obj):
    return str(int(hashlib.md5(obj.to_json().encode('utf-8')).hexdigest(), 16) % 10**25)



