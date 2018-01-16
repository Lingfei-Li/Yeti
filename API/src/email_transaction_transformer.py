import outlook_service
from auth import LoginAuthorizer, OutlookAuthorizer
import email_parser
import time
from dynamodb import transactions_table, logins_table, tokens_table
from bs4 import UnicodeDammit

from botocore.exceptions import ClientError


def update_user_transactions(jwt_token, email):

    # LoginAuthorizer.verify_jwt_token(jwt_token, email)
    #valid_access_token = get_latest_token(email)

    access_token = "EwA4A8l6BAAU7p9QDpi/D7xJLwsTgCg3TskyTaQAAVemNLwR4sMCVSs9uIdYmjV6K0rNwOOgA/BRSHZlsjYi/7AY9x95ajh2y46SkHzjF+zG4q8Uw045ApnMWWVKv0NrC7ZOcDMrm9F15qhw8BlpKlI0hxEAyEBcZ+2a7Obsq75cRiv/7M5+hfU+JGB60dQGZf9kKrTNeWd4e9QCTCTEl7JJaltx3jSb4YNtas68u+ND/x7RN5KzfqlOT0ceG5FNzGcVK0FjHHB6lFbF0hUWmhwV1WW7nmzOCJElnFSmnpRYHjtSTS0Tl6zEHP2vNS/WBso2w1w7QIq4U6xfa1Sonf1TATT5Nw+FNk+C8J5BYSDLD2Uq0OYWEY8FS3uTKDMDZgAACOT0SjhNC0gJCALO33Taq8LXi+eSBN6XyMLc/BiP1lSBdPSIFxrikbVMPEbKAYA3B/ZPln2VUZUIG1YDMBbsAEz+zJoRd+8cgc3OojBsPhGS3QHKCAV+n8EElKtupg8PaiksroHVnGVdwYEGiGmncZZ1EzgeGu/do0RcwD3Ogdlc75Ps9eOMgiNO9YLF3f8L1HkG361u/1N77nECxflLCGIixG09UniRVjp2evt1mIUn+WGqrkuET0i9MAVGa56h7SlpKP1U7/8pAqIe1rOhKiCX6dUfYYjSQscVpiHtNSnbDtVxxf5TUEjfaSk3npSwBDJLdpqKz5rfSV9ba+/FAgNw+OPleOtpHJeOXnwzLGn6pMIcwe1EZeWwdczzHp31PfJYmvqT09+qd5S3qeuqn4K1EXGMv35AKIl/srb49yAPvLzNHOCZ5BzOCc5OMLIiQZy1yZ/REdIZzkE78n2hsyZQwfEvo8gG2FB0CdC0vMxke07/3/ufmHChubjH3da1l8F22C33/6xUcMfwq+En69Y3Y4XhJhmvOs+MU8BsuFpA8ICHkPO4CU6TKexTnKmTpU2XZU9vhpOdRbVRD0Eezz+2Ghx6Qe62ITRgAMefj54gR6jqvAH1liE9DfKSA+XJV64itprWx69BUeXTMXqR80J5Gfe5FOvQIkjudLyknA9sf3f6Fhtg6wZF05b+/1YKd02/OQI="

    user_email = outlook_service.get_me(access_token)["userPrincipalName"]
    # print user_email
    #     ["userPrincipalName"]
    timestamp = get_latest_timestamp_from_table(user_email)
    # print timestamp

    response = outlook_service.get_messages_received_after(access_token, user_email, timestamp)
    if 'value' not in response:
        raise ValueError(response)
    emails_since_last_timestamp = response['value']
    for email in emails_since_last_timestamp:
        transform_email_to_transaction(email)

    record_last_timestamp(emails_since_last_timestamp)

def get_latest_token(email):
    current_time = time.time()

    response = tokens_table.get_item(
        Key={
            'Email': email
        }
    )['Item']

    if current_time > response['ExpirationUnixTimestamp']:
        refresh_response = OutlookAuthorizer.refresh_token(response['RefreshToken'])
        print refresh_response.data







def get_latest_timestamp_from_table(user_email):
    return "2014-09-01T00:00:00Z"

def record_last_timestamp(emails):
    print "last timestamp updated to db"

def transform_email_to_transaction(email):
    email_body = email['body']['content']
    print "-----"
    email_parser.parse(email_body)
    print "****"




