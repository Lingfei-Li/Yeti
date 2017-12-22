import json

CORS_HEADERS = {
    "Access-Control-Allow-Headers": "Content-Type,Authorization,X-Amz-Date,X-Api-Key,X-Amz-Security-Token",
    "Access-Control-Allow-Methods": "DELETE,GET,HEAD,OPTIONS,PATCH,POST,PUT",
    "Access-Control-Allow-Origin": "*"
}


def ok(data):
    return response(200, data)


def client_error(error):
    return response(400, error)


def internal_error(error):
    return response(500, error)


def response(status_code, data):
    return {
        'statusCode': status_code,
        'headers': CORS_HEADERS,
        'body': json.dumps(data)
    }
