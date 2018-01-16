import json
import dynamodb
from test_data import transactions, logins
import random
import pprint

date_timestamps = [1513468800,  # 12/17/2017
                   1514160000,  # 12/25/2017
                   1514678400,  # 12/31/2017
                   1515801600  # 1/13/2018
                   ]

users = [
    {
        'id': 'John-Doe',
        'name': 'John Doe'
    },
    {
        'id': 'John-1961',
        'name': 'John F. Kennedy'
    },
    {
        'id': 'Homer123',
        'name': 'Homer Simpson'
    },
    {
        'id': 'Tom-Jerry-2',
        'name': 'Tom and Jerry'
    },
    {
        'id': 'yeti2018',
        'name': 'Yeti Amazon'
    }
]

locations = [
    'Stevens',
    'Snoqualmie',
    'Crystal Mountain',
    'Mt Rainier'
]

data_count = 100

random.seed(0)

for i in range(data_count):
    timestamp = random.choice(date_timestamps) + random.randint(0, 24 * 60 * 60)
    friend = random.choice(users)
    friend_id = friend['id']
    friend_name = friend['name']
    ticket_count = random.randint(1, 10)
    payment_amount = ticket_count * 59
    location = random.choice(locations)
    data = {
        "TransactionId": "payment-" + str(i),
        "TransactionPlatform": "venmo",
        "UserEmail": "yeti-dev@outlook.com",
        "UserId": "Yeti-Dev",
        "TransactionUnixTimestamp": timestamp,
        "Amount": payment_amount,
        "StatusCode": 0,
        "FriendId": friend_id,
        "FriendName": friend_name,
        "Comments": "1 Ski Tickets for " + location,
        "SerializedUpdateHistory": "[]"
    }
    response = dynamodb.transactions_table.put_item(
        Item=data
    )

    pp = pprint.PrettyPrinter()
    pp.pprint(data)

# for item in transactions:
#     print("Data:", json.dumps(transactions))
#     response = dynamodb.transactions_table.put_item(
#         Item=item
#     )
#     print(response)
#
# for item in logins:
#     print("Data:", json.dumps(logins))
#     response = dynamodb.logins_table.put_item(
#         Item=item
#     )
#     print(response)
