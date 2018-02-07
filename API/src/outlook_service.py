import os

import requests
import uuid
import json
import yeti_exceptions
import dateutil.parser

# graph_endpoint = 'https://graph.microsoft.com/v1.0{0}'
outlook_api_endpoint = 'https://outlook.office.com/api/v2.0{0}'

notification_url = os.environ['NotificationWebhookUrl'] if 'NotificationWebhookUrl' in os.environ else "https://fxsrb1p4k2.execute-api.us-west-2.amazonaws.com/prod/payment/outlook-notification"


# Generic API Sending
def make_api_call(method, url, token, user_email, payload=None, parameters=None):
    # Send these headers with all API calls
    headers = {'User-Agent': 'python_tutorial/1.0',
               'Authorization': 'Bearer {0}'.format(token),
               'Accept': 'application/json',
               'X-AnchorMailbox': user_email}

    # Use these headers to instrument calls. Makes it easier
    # to correlate requests and responses in case of problems
    # and is a recommended best practice.
    request_id = str(uuid.uuid4())
    instrumentation = {'client-request-id': request_id, 'return-client-request-id': 'true'}

    headers.update(instrumentation)

    response = None

    if method.upper() == 'GET':
        response = requests.get(url, headers=headers, params=parameters)
    elif method.upper() == 'DELETE':
        response = requests.delete(url, headers=headers, params=parameters)
    elif method.upper() == 'PATCH':
        headers.update({'Content-Type': 'application/json'})
        response = requests.patch(url, headers=headers, data=json.dumps(payload), params=parameters)
    elif method.upper() == 'POST':
        headers.update({'Content-Type': 'application/json'})
        response = requests.post(url, headers=headers, data=json.dumps(payload), params=parameters)

    return response


def get_me(access_token):
    """
    Get the user profile with the OAuth access token

    :param access_token: the Outlook OAuth access token
    :return: the user object that contains attributes like 'mail'
    :raise: yeti_exceptions.YetiAuthTokenExpiredException()
    :raise: yeti_exceptions.OutlookApiErrorException
    """
    get_me_url = outlook_api_endpoint.format('/Me')

    query_parameters = {'$select': 'DisplayName,EmailAddress'}

    r = make_api_call('GET', get_me_url, access_token, "", parameters=query_parameters)

    try:
        response = r.json()
    except Exception as e:
        raise yeti_exceptions.OutlookApiErrorException("Failed to transform response text to JSON: {}".format(e))

    if r.status_code != requests.codes.ok or ('error' in response and response['error']):
        if 'code' in response['error'] and response['error']['code'] == 'InvalidAuthenticationToken':
            raise yeti_exceptions.YetiAuthTokenExpiredException()
        else:
            raise yeti_exceptions.OutlookApiErrorException("Failed to get user profile. Response: {}".format(response))
    return response


def get_messages(access_token, user_email, last_processed_date_str_iso8601=None):
    """
    Get the user profile with the OAuth access token

    :param access_token: the Outlook OAuth access token
    :param user_email: the email address of the user
    :param last_processed_date_str_iso8601: the IOS8601 formatted date string for the last processed email date
    :return: an array of email objects
    :raise: yeti_exceptions.YetiAuthTokenExpiredException
    :raise: yeti_exceptions.OutlookApiErrorException
    """
    get_messages_url = outlook_api_endpoint.format('/me/mailfolders/inbox/messages')

    # '$filter': 'ReceivedDateTime gt ' + timestamp + ' and ' + 'from eq \'venmo@venmo.co\'',
    # The query parameter '$filter' is not supported with '$search'." therefore need to manually filter all email from venmo

    select_expr = 'receivedDateTime,subject,body,from'
    filter_expr = '(From/EmailAddress/Address eq \'venmo@venmo.com\')'
    if last_processed_date_str_iso8601 is not None:
        # Note the insertion order of the new expression. Fields in 'orderby' must come first in 'filter' and must be in the same order
        # For details: https://stackoverflow.com/a/41026120/1387710
        filter_expr = '(ReceivedDateTime gt {}) and '.format(last_processed_date_str_iso8601) + filter_expr
        order_by_expr = 'receivedDateTime DESC'
    else:
        # Fields in 'order by' must be present in 'filter', otherwise Outlook complains "Inefficient Error".
        # For details: https://stackoverflow.com/a/41026120/1387710
        order_by_expr = 'From/EmailAddress/Address DESC'

    query_parameters = {'$filter': filter_expr,
                        '$select': select_expr,
                        '$orderby': order_by_expr
                        }

    r = make_api_call('GET', get_messages_url, access_token, user_email, parameters=query_parameters)

    try:
        response = r.json()
    except Exception as e:
        raise yeti_exceptions.OutlookApiErrorException("Failed to transform response text to JSON: {}".format(e))

    if r.status_code != requests.codes.ok or ('error' in response and response['error']):
        if 'code' in response['error'] and response['error']['code'] == 'InvalidAuthenticationToken':
            raise yeti_exceptions.YetiAuthTokenExpiredException()
        else:
            raise yeti_exceptions.OutlookApiErrorException("Failed to get email messages. Response: {}".format(response))
    if 'value' not in response:
        raise yeti_exceptions.OutlookApiErrorException("Failed to get email messages. 'value' is empty. Response: {}".format(response))
    new_emails = response['value']
    return new_emails


def get_message_for_id(message_id, access_token, user_email):
    """
    Get the message with the message id

    :param message_id: the id to retrieve the message
    :param access_token: the Outlook OAuth access token
    :param user_email: the email address of the user
    :return: the email message in JSON. contains "Body", "Sender", etc.
    :raise: yeti_exceptions.YetiAuthInvalidTokenException
    :raise: yeti_exceptions.OutlookApiErrorException
    """

    url = outlook_api_endpoint.format('/Me/MailFolders/Inbox/Messages/{}'.format(message_id))

    r = make_api_call('GET', url, access_token, user_email)

    try:
        response = r.json()
    except Exception as e:
        raise yeti_exceptions.OutlookApiErrorException("Failed to transform response text to JSON: {}".format(e))

    if r.status_code != requests.codes.ok or ('error' in response and response['error']):
        if 'code' in response['error'] and response['error']['code'] == 'InvalidAuthenticationToken':
            raise yeti_exceptions.YetiAuthInvalidTokenException()
        else:
            raise yeti_exceptions.OutlookApiErrorException("Failed to get email messages. Response: {}".format(response))

    return response


def create_notification_subscription(access_token, user_email):
    url = "https://outlook.office.com/api/v2.0/me/subscriptions"

    payload = {
        "@odata.type": "#Microsoft.OutlookServices.PushSubscription",
        "Resource": "https://outlook.office.com/api/v2.0/me/messages",
        "NotificationURL": notification_url,
        "ChangeType": "Created",
        "ClientState": "c75831bd-fad3-4191-9a66-280a48528679"
    }

    response = make_api_call('POST', url, access_token, user_email, payload)
    if response.status_code != requests.codes.created:  # success response is 201
        raise yeti_exceptions.OutlookApiErrorException('Failed to create new outlook notification subscription. status code: {}'.format(response.status_code))
    try:
        response_content = json.loads(response.content.decode('utf-8'))
        subscription_id = response_content['Id']
        subscription_expiry_datetime_isoformat = response_content['SubscriptionExpirationDateTime']
        subscription_expiry_datetime = dateutil.parser.parse(subscription_expiry_datetime_isoformat)

        return subscription_id, subscription_expiry_datetime
    except Exception as e:
        raise yeti_exceptions.OutlookApiErrorException(e)


def delete_subscription(access_token, user_email, subscription_id):
    url = "https://outlook.office.com/api/v2.0/me/subscriptions('{}')".format(subscription_id)

    response = make_api_call('DELETE', url, access_token, user_email)

    if response.status_code != requests.codes.no_content:  # success response is 204
        raise yeti_exceptions.OutlookApiErrorException()


def renew_subscription(access_token, user_email, subscription_id):
    url = "https://outlook.office.com/api/v2.0/me/subscriptions/{}".format(subscription_id)

    payload = {
        "@odata.type": "#Microsoft.OutlookServices.PushSubscription"
    }

    response = make_api_call('PATCH', url, access_token, user_email, payload)
    if response.status_code != requests.codes.ok:   # success response is 200
        raise yeti_exceptions.OutlookApiErrorException()

    try:
        response_content = json.loads(response.content.decode('utf-8'))
        subscription_id = response_content['Id']
        subscription_expiry_datetime_isoformat = response_content['SubscriptionExpirationDateTime']
        subscription_expiry_datetime = dateutil.parser.parse(subscription_expiry_datetime_isoformat)

        return subscription_id, subscription_expiry_datetime
    except Exception as e:
        raise yeti_exceptions.OutlookApiErrorException(e)

