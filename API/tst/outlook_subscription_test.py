import dateutil.parser
import requests
import uuid
import json
import yeti_exceptions
import outlook_service


import requests
import uuid
import json

outlook_api_endpoint = 'https://outlook.office.com/api/v2.0{0}'
my_token = 'EwAYA+l3BAAUWm1xSeJRIJK6txKjBez4GzapzqMAAXy5FYoxqemCbO/0/U/qp+MNv1WXwnKBFHGltp7VJ/ro9o0NHkINV2pejEXLz0AdAOWfjAnLigRsNAAqhnw4aotB1K3pXwGhtUaLrMBoUACMC8W2RoVvTToKxjvDvQWZ/V2NHYpLfZBsrJiF+mrmVSSAbauxStYcH7/MxyiYdw/5c3+gEtgTFjsX7C2HbGSOdPnKE6wyinjVqoGoUvcyqs1nv/u+/sBRxHw/u+3shqlCueI+1v1UYlfzWtqXHbx5vlj+poH26pBcui73FnZfbpHJBvHoDfI0alotSpF4oh3OHlwiTa6B2Vv/XLzHNdmJKiox524E6HTNIHkdxClkUzwDZgAACIxsMu5PjHuU6AFDxt3fF7kQcie8M9zkznGhf3HMMxJ+BxPJ0Zu1x5MEbe1ZiHMTwvfCwyMW5JeBI15WD0qpGnJdhfom2ABWP0/+rbbSzxcbowZls+R4Nim87LxNx2qSacQr5Ok14fZo2MbZu2UWWlFXZYC8jZSVr6wkO8EcZQi1Nbd6sGe2bAVynT6l/oFWfMcwugrteJCQhwNUA4LQqY6rn2Umzo4qa3xhDqW8QLP9WQZRk6KU763rIJIAKybrM+5GB00+HkEV44r4nIe6DUMV1AYOfDSK3BDBg2z3GFCgSr8E8NbgvGxbyfFm0BUYt0ywy+F2goa61NWal8IikVjoe+q37oA83cu598x5CNjgijDgXxag7S6eNlxUzl68RTfjvtKATSA6ej7uzwOjA+EVO6OEQgZTdxN+EtZtK9rS0eX+SXBJDuIYLZ6R6jMeH+Jri3sUxFvL6DAPqA1XhM6AWEUKwmpAfKCfyngeW3n4QGBVstdbZbupK1MjLh4L3Xm0RKKs56z/R1cWzZ5rGqNjvMYqN+QyEyO+coBWN1LpWJouK9DoUYAEA3Vl3vela1DWyvQOoKQTDsbAL2Uy/T0S3JPdW39wIc8nGLce+oLbj3hlcVf/A9+H4Y7cCf2A8XMkFFeKt8NXei8obbTBJjjnohwC'
my_email = "yeti-dev@outlook.com"
# my_subscription_id = 'RDhFMkQ2RDMtRkMzOS00QTQ3LTg2RjYtMjNDODE2RUFFMUFFXzAwMDM0MDAxLTA4ODQtQTM3NS0wMDAwLTAwMDAwMDAwMDAwMA=='
my_subscription_id = 'RDk5NDk3MzItQTgyQy00RjE0LTk5RDctQzM0RjNEMDkxNzgxXzAwMDM0MDAxLTA4ODQtQTM3NS0wMDAwLTAwMDAwMDAwMDAwMA=='
# my_subscription_id = 'OUNEOTk4M0EtRTNFQi00NUIzLTg2M0EtRUIyN0E1MkNFOEJCXzAwMDM0MDAxLTA4ODQtQTM3NS0wMDAwLTAwMDAwMDAwMDAwMA=='


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
    instrumentation = { 'client-request-id' : request_id,
                        'return-client-request-id' : 'true' }

    headers.update(instrumentation)

    response = None

    if method.upper() == 'GET':
        response = requests.get(url, headers = headers, params = parameters)
    elif method.upper() == 'DELETE':
        response = requests.delete(url, headers = headers, params = parameters)
    elif method.upper() == 'PATCH':
        headers.update({ 'Content-Type' : 'application/json' })
        response = requests.patch(url, headers = headers, data = json.dumps(payload), params = parameters)
    elif method.upper() == 'POST':
        headers.update({ 'Content-Type' : 'application/json' })
        response = requests.post(url, headers = headers, data = json.dumps(payload), params = parameters)

    return response


def send_message_to_recipient(recipient_email_address, message_subject="Testing", message_body="Testing message"):
    message = {
        "Message": {
            "Subject": message_subject,
            "Body": {
                "ContentType": "Text",
                "Content": message_body
            },
            "ToRecipients": [
                {
                    "EmailAddress": {
                        "Address": recipient_email_address
                    }
                }
            ],
            "Attachments": [
            ]
        },
        "SaveToSentItems": "true"
    }

    url = 'https://outlook.office.com/api/v2.0/me/sendmail'

    r = make_api_call('POST', url, my_token, my_email, message)

    if r.status_code == requests.codes.ok:
        print(r.json())
        return r.json()
    else:
        print("{0}: {1}".format(r.status_code, r.text))
        return "{0}: {1}".format(r.status_code, r.text)


def get_message_by_id():
    id='AQMkADAwATM0MDAAMS0wODgANC1hMzc1LTAwAi0wMAoARgAAA9crIn1O2lBMtQum7-80kOAHALkUBuCVBlJBjgyeckJKxPEAAAIBDAAAALkUBuCVBlJBjgyeckJKxPEAAAATn_KuAAAA'
    get_messages_url = outlook_api_endpoint.format('/Me/MailFolders/Inbox/Messages/{}'.format(id))

    r = make_api_call('GET', get_messages_url, my_token, my_email)

    if (r.status_code == requests.codes.ok):
        print(r.json())
        return r.json()
    else:
        print("{0}: {1}".format(r.status_code, r.text))
        return "{0}: {1}".format(r.status_code, r.text)


def get_my_messages():
    get_messages_url = outlook_api_endpoint.format('/Me/MailFolders/Inbox/Messages')

    query_parameters = {'$top': '10',
                        '$select': 'ReceivedDateTime,Subject,From',
                        '$orderby': 'ReceivedDateTime DESC'}

    r = make_api_call('GET', get_messages_url, my_token, my_email, parameters = query_parameters)

    if (r.status_code == requests.codes.ok):
        print(r.json())
        return r.json()
    else:
        print("{0}: {1}".format(r.status_code, r.text))
        return "{0}: {1}".format(r.status_code, r.text)


def create_subscription():
    url = "https://outlook.office.com/api/v2.0/me/subscriptions"

    payload = {
        "@odata.type": "#Microsoft.OutlookServices.PushSubscription",
        "Resource": "https://outlook.office.com/api/v2.0/me/messages",
        "NotificationURL": "https://fxsrb1p4k2.execute-api.us-west-2.amazonaws.com/prod/payment/outlook-notification",
        "ChangeType": "Created",
        "ClientState": "c75831bd-fad3-4191-9a66-280a48528679"
    }

    response = make_api_call('POST', url, my_token, my_email, payload)

    import pprint
    pp = pprint.PrettyPrinter()

    print(response)

    response_content = response.content

    subscription_id = json.loads(response_content.decode('utf-8'))['Id']
    subscription_expiry_datetime_isoformat = json.loads(response_content.decode('utf-8'))['SubscriptionExpirationDateTime']
    subscription_expiry_datetime = dateutil.parser.parse(subscription_expiry_datetime_isoformat)

    pp.pprint(subscription_id)
    pp.pprint(subscription_expiry_datetime)


def delete_subscription():
    url = "https://outlook.office.com/api/v2.0/me/subscriptions('{}')".format(my_subscription_id)

    response = make_api_call('DELETE', url, my_token, my_email)

    print(response)

    import pprint
    pp = pprint.PrettyPrinter()
    print(response.text)
    pp.pprint(response.headers)


def renew_subscription():
    url = "https://outlook.office.com/api/v2.0/me/subscriptions/{}".format(my_subscription_id)

    payload = {
        "@odata.type": "#Microsoft.OutlookServices.PushSubscription"
    }

    response = make_api_call('PATCH', url, my_token, my_email, payload)

    print(response)

    import pprint
    pp = pprint.PrettyPrinter()

    response_content = response.content

    subscription_id = json.loads(response_content.decode('utf-8'))['Id']
    subscription_expiry_datetime_isoformat = json.loads(response_content.decode('utf-8'))['SubscriptionExpirationDateTime']
    subscription_expiry_datetime = dateutil.parser.parse(subscription_expiry_datetime_isoformat)

    pp.pprint(subscription_id)
    pp.pprint(subscription_expiry_datetime)


send_message_to_recipient("cslilingfei@outlook.com")
# create_subscription()
# renew_subscription()
# delete_subscription()
# get_my_messages()
# new_emails = outlook_service.get_messages(my_token, my_email)
# print(new_emails)
# get_message_by_id()

