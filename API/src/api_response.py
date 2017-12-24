import json

CORS_HEADERS = {
    "Access-Control-Allow-Headers": "Content-Type,Authorization,X-Amz-Date,X-Api-Key,X-Amz-Security-Token",
    "Access-Control-Allow-Methods": "DELETE,GET,HEAD,OPTIONS,PATCH,POST,PUT",
    "Access-Control-Allow-Origin": "*"
}


def ok(data):
    return response(200, json.dumps(data))


def ok_no_data(message):
    return response(200, {
        "message": message
    })


def client_error(error_msg):
    return response(400, {
        'error': error_msg
    })


def internal_error(error_msg):
    return response(500, {
        'error': error_msg
    })


def response(status_code, data):
    return {
        'statusCode': status_code,
        'headers': CORS_HEADERS,
        'body': json.dumps(data)
    }
