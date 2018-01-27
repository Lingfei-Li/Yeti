import decimal
import boto3
import os
from base64 import b64decode


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


decrypted_data = {}


def decrypt_for_key(key):
    if key in decrypted_data:
        return decrypted_data[key]
    if key not in os.environ:
        return None
    encrypted_val = os.environ[key]
    decrypted_val = boto3.client('kms').decrypt(CiphertextBlob=b64decode(encrypted_val))['Plaintext']
    decrypted_data[key] = decrypted_val
    return decrypted_val

