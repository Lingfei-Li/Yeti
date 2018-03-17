import requests
import uuid

client_id = '1420c3c4-8202-411f-870d-64b6166fd980'
client_secret = 'rFSZQ47995(}]hmfsbqXDL%'

# Constant strings for OAuth2 flow
# The OAuth authority
authority = 'https://login.microsoftonline.com'

# The authorize URL that initiates the OAuth2 client credential flow for admin consent
authorize_url = '{0}{1}'.format(authority, '/common/oauth2/v2.0/authorize?{0}')

# The token issuing endpoint
token_url = '{0}{1}'.format(authority, '/common/oauth2/v2.0/token')

# The redirect url must align with the redirect url used for signin
test_redirect_url = 'http://localhost:8000/tutorial/gettoken/'
redirect_url = 'https://auth.expo.io/@drinkiit/yeti-mobile'

# The scopes required by the app
scopes = ['openid',
          'offline_access',
          'User.Read',
          'Mail.Read',
          'Mail.Send',
          'Calendars.Read',
          'Contacts.Read']

graph_endpoint = 'https://graph.microsoft.com/v1.0{0}'


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


def get_my_messages(access_token, user_email):
    get_messages_url = graph_endpoint.format('/me/mailfolders/inbox/messages')

    # Use OData query parameters to control the results
    #  - Only first 10 results returned
    #  - Only return the ReceivedDateTime, Subject, and From fields
    #  - Sort the results by the ReceivedDateTime field in descending order
    query_parameters = {"$top": "10",
                        # '$filter': 'ReceivedDateTime gt 2014-09-01T00:00:00Z and From eq \'asd\'',
                        # '$filter': 'Subject eq \'asd\'',
                        "$filter": "From/EmailAddress/Address eq 'chloeosness@allstate.com'"
                        # '$orderby': 'receivedDateTime DESC'
                        }

    r = make_api_call('GET', get_messages_url, access_token, user_email, parameters = query_parameters)

    if (r.status_code == requests.codes.ok):
        return r.json()
    else:
        return "{0}: {1}".format(r.status_code, r.text)


def mail():
    access_token = 'EwBAA8l6BAAU7p9QDpi/D7xJLwsTgCg3TskyTaQAAfIk1Lt0lQg59IFMN+AXYrIp+VIaUQDvoUs1z6KhetQizfF3B0lUh3z0LthlGbJq+kcky8qPPSlqcvQyvXfhBym4wnJUOjq6QA/JwMpm27XlN6r+BtWpliUKUBUJK9WoHCYeGojUlx9xlHhuU7LxkI5MNBMt3yIKwxfI7N2Okk9wftnbQCIXGR/jh4H/OfYP6P1aIYXESGPgiqWlRqji6cN9YBMiVCD8CIo8aRGgEcQHbNaf6DiXoGXL85uPJA5MUNGw/P4vlQiB5z0xvLI/ZM9gHv18/Ex1lR9COT0jCHfL3l/ev4wdVi9V2aE00lMiMXWqUBZkcqGHb6oP6sEUrUUDZgAACFfay3zISPA8EAIZtJPJ1mn/BdQeOzep5UOYVSxRkIkYjifALRIsMPncC+pgenXqzdwd1kHyY/zlYBdG4vI6Ceo/AvbA1xqN9xcEpmWU5d7ulimMQ2zVoU6f7jXuY+nkse6rZQU2CFxj0CkFTG9qdRQz4o3X9inOFNkTRaOiXAL/bkXUlaxHS4iCc6W9UkXc62CUlDumqsRhefK5Pumg5eMDseD/vb3K06wGC5b4YHU5Vqe5qOFvUrBScQiCFb4eJKce7Aw1GhoH9Y835O3lZyXMovf0s84lBeBoe0Ha88ipPYWxftKweGKZVqJ09ZF0dvBJgefITcMGtvEhEIBohcBEsjgoX2Aoz8MpjOD0bIXGHXTo86wxPsKtO9KFcKQSRPQcgWrJTa5AKWe85XwbJL9Bygjh4b4/Hu89LIxRiQLHJN64MFR1C8O9g2Cz+ZtoN7mB7iV4AT1gYSnjtvuykZKzVCOb96I8uIlyLLHW4IgLB3UofNr8WdY+VwAwmVsR0ncghJ7EQeJ6d5SyZRCrBUL+K9nYa215h6N4EZfZOa0ggamDXtCYQrC0ke64LdY6QXlF3cSve1XRyb212iW6zYwThlQX/qutDd20r+hYnqliRjobyge7WM5a4DcdoPzoKxihQWFp/05g5qw8w3CmAmiXfQD0eCLz4BUoFL5cw01FosT8tjoGOFYnDk4AGA31NuSnrSFTp8cr/BBBAg=='
    user_email = 'cslilingfei@outlook.com'
    # If there is no token in the session, redirect to home
    messages = get_my_messages(access_token, user_email)
    import pprint
    pp = pprint.PrettyPrinter()
    pp.pprint('Messages: {0}'.format(messages))

mail()