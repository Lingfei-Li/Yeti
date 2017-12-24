import json
from src import dynamodb
from tst.test_data import transactions, logins

for item in transactions:
    print("Data:", json.dumps(transactions))
    response = dynamodb.transactions_table.put_item(
        Item=item
    )
    print(response)


for item in logins:
    print("Data:", json.dumps(logins))
    response = dynamodb.logins_table.put_item(
        Item=item
    )
    print(response)





