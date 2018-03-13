import json
import yeti_utils_common

CORS_HEADERS = {
    "Access-Control-Allow-Headers": "Content-Type,Authorization,X-Amz-Date,X-Api-Key,X-Amz-Security-Token",
    "Access-Control-Allow-Methods": "DELETE,GET,HEAD,OPTIONS,PATCH,POST,PUT",
    "Access-Control-Allow-Origin": "*"
}


def ok(data, headers=None):
    data_json = json.dumps(yeti_utils_common.replace_decimals(data))
    return response(200, data_json, headers)


def ok_no_data(message="success", headers=None):
    return response(200, {
        "message": message
    }, headers)


def client_error(error_msg, headers=None):
    return response(400, {
        'error': error_msg
    }, headers)


def not_found(error_msg, headers=None):
    return response(404, {
        'error': error_msg
    }, headers)


def internal_error(error_msg, headers=None):
    return response(500, {
        'error': error_msg
    }, headers)


def response(status_code, data, headers=None):
    data_json = json.dumps(yeti_utils_common.replace_decimals(data))
    return {
        'statusCode': status_code,
        'headers': CORS_HEADERS if headers is None else headers,
        'body': data_json
    }
