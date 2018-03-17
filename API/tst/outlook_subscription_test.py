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
my_token = 'EwAQA+l3BAAUWm1xSeJRIJK6txKjBez4GzapzqMAARWOYMnkuK+zpcKsdn8hm7i2Zv35Zx1DHK9n12Upb4zv10H0HEuXUBnkvZqrFHVP6yV0EYXP9DyyB3f0Gkl9zyowoaJxduKEtUlDTNka2GTyDlsS0/GyT0bxszux9X6ffsPHdBkK+6/Fp/m+LFN9IpX9S1WDz10zC7GWjn4/Ji1AUAccFwHqN6rpQlQLEIpFa50TW0m60K6rMMo493bZABkkhjTe/BTpo1PRWW8P/dAGJIOAKb32Of4NG0ZgF7Vh5tZ3ETAIO3e5zlPpcgI6MP4S0Rk/+uYit1DeSmQ6Wo7fOeZpAc9UjjnG+XbYC1uWbKAQwbcC1UtrcxWC86n3YL8DZgAACH/wwWCNnwu54AGZl9Tq56beOikxRnCcGRJ8+1IR9pycq097lE/rbtULldhYLx6g6XlLQ+D1CPa1/b4iviV1i4fBVgdGlzUP2zWXboPFSbuL+fM/ZYFRqau6V8d6xOe3u63tiMAXCMugXhNWJF9/elWGv/ND4gE3ycVn0C5cfya+0ctjKRxLhKuEnijYstIJNSuMXnfrX7qPTajXFZ6Bd0fbKw/Sdk0Ze0ekrOhno66wkIxDkBievEJrRGqcj0LIknVA5nYXj/muzE62VPKxC99KALJdjDN3FjDkKeTAHpY7djotEPJjvhtaMObX3cUXnRk/sL6xaYEblg1lpA81aUb5vQ+ePOLyj9etn6cXMLJj7sunIh+cEcAxwOghVlNkFLAP26GwEmQPL68VqLRIkOXGgrBqFSzQ9dK7qxiiXYsxCPepy8JStNNgNrswytNjmBYLke1+zC5FELM7W3DORsOvq0lb6d5EzUi4BeoHyg8b3qkpDjyld9CXg6TQsJgdThixFNaGxWvZ8m6E6AwcJNbyI2zT/G1sI6QXZntqskrxjYSvULB5dS76n8LGGd0T6RmGXRRzUpZGTN10Fhep1kjIql3sVOrWY+amCrmn6edf31jUi9PvnUN2jEdnRmuZhBVnORtc8vsL0nQUAg=='
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


def send_message_to_recipient(recipient_email_address):
    message = {
        "Message": {
            "Subject": "Meet for lunch?",
            "Body": {
                "ContentType": "Text",
                "Content": "This is an automated email from yeti!"
            },
            "ToRecipients": [
                {
                    "EmailAddress": {
                        "Address": "lzexi@amazon.com"
                    }
                },
                {
                    "EmailAddress": {
                        "Address": "cslilingfei@outlook.com"
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

