import json

CORS_HEADERS = {
    "Access-Control-Allow-Headers": "Content-Type,Authorization,X-Amz-Date,X-Api-Key,X-Amz-Security-Token",
    "Access-Control-Allow-Methods": "DELETE,GET,HEAD,OPTIONS,PATCH,POST,PUT",
    "Access-Control-Allow-Origin": "*"
}


def ok(data, headers=None):
    return response(200, json.dumps(data), headers)


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
    return {
        'statusCode': status_code,
        'headers': CORS_HEADERS if headers is None else headers,
        'body': json.dumps(data)
    }
