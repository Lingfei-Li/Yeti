import json
from src import dynamodb

with open('./test_data.json') as test_data_file:
    test_data = json.load(test_data_file)

for item in test_data:
    print("Data:", json.dumps(test_data))
    response = dynamodb.transactions_table.put_item(
        Item=item
    )
    print(response)







