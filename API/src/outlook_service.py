# Copyright (c) Microsoft. All rights reserved. Licensed under the MIT license. See LICENSE.txt in the project root for license information.
import requests
import uuid
import json

graph_endpoint = 'https://graph.microsoft.com/v1.0{0}'


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
    get_me_url = graph_endpoint.format('/me')

    # Use OData query parameters to control the results
    #  - Only return the displayName and mail fields
    query_parameters = {'$select': 'displayName,mail'}

    r = make_api_call('GET', get_me_url, access_token, "", parameters=query_parameters)

    if r.status_code == requests.codes.ok:
        return r.json()
    else:
        return "{0}: {1}".format(r.status_code, r.text)


def get_messages(access_token, user_email, last_processed_date_str_iso8601=None):
    get_messages_url = graph_endpoint.format('/me/mailfolders/inbox/messages')

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

    if r.status_code == requests.codes.ok:
        return r.json()
    else:
        return "{0}: {1}".format(r.status_code, r.text)
