import re
from bs4 import BeautifulSoup

import boto3
from boto3.dynamodb.conditions import Key

import outlook_service
import yeti_utils_email



access_token ='EwAYA+l3BAAUWm1xSeJRIJK6txKjBez4GzapzqMAAVBU+J3ozh3Et9JIySCe+3L31lNuAEUGsJFWjxuvNaoWvTXJf32DIhDlNFOzzeWBm/zyzRgvGB2cqYpKHxsG8rs3ZwoFKJr2C3JW2oJKhxuB82geFeusKAN1D7syPB1sXArA0owOB6bGnDaBkVxlF6is1G2CUH3hTPsXmylkBzi77M77U4aYSTF/jay1swnrS6i1I85ZnDV3V33ZjXzoAvdWUoKJh27F+KhylMp+qU9Ksrpqkmlc+Y9STwqbXE3f/uaaZTPKftbIxIWF9ZX3h911aiq65N4WofqIRdPvINVTbxaLckFRkRyHShbvjfs586tHM6DMa1GA8gZaHTqleRQDZgAACLpSPV2pg9p16AFYf+ykEYR9d3t8zIwu9VyVF84frX4gpe11+u+9teWBia3pChp7+xpw4Iis2jQmq9JD25QDfJOSE6jsDPpe03wg482TuwdqxZ3IgpuXDCTnya6UYlfdtuGl3IQZlXdfdpWNjGQ1vqJuYqQv0FHcu+R1OyACYeTodqvxugNehaZ9A3FMTun3UF11SGmHDXGNaytEWLMKFfmCV7pz3JodZfKiJv2bdHLw/+AdX/fLppv7T+v3UhSoG+bpgNHgw+KUMXVu86lF2SJjFPdWAXdhGsY2g2ezVQ71/vnUMpjsR2XVLVyH5YdAS8QOyiczx5K8SyaE2tST62lXNTwfjuzFr7rdnzqyvIC6moEXRK3Cl4kuCMD26Bi11VAkGaQmgA93t4mP849/T50wiw61omfuSa23lNAqkEjaEdV9m9825UP6n7ljnFK1xYuZM6kA0Yfr2Gm1onXlmN7VuPp+wPkV/kFz4OkexjcOw8LbhZSKxkkz5ZysXjJ4Gr6UG7G4QxdMsstPcFf1RoOR3Cv4u5D/Uy0QPyi31ErSNDcb1Uy6f12pVY4fxiruv0h096RFpO7nRcKEk6/bg890HyNMSN79WfEkTc0qeubeWGUK3wh8yCWN5ldpD1K6ZmRwS4EyKCm1fP7NERpnGR9SpRgC'
user_email='yeti-dev@outlook.com'

messages = outlook_service.get_messages(access_token, user_email)

import pprint
pp = pprint.PrettyPrinter()

m = messages[-1]
body = m['Body']['Content']
subject = m['Subject']
pp.pprint(body)
pp.pprint(subject)

order_id_regex = "YetiOrder#([^#]+)#"
# m = re.search(story_id_regex, m['Body']['Content'])
# b = 'f="https://venmo.com/story/5a519c395a877f6e38eb1903?login=1" '
m = re.search(order_id_regex, body)

def append_key_value(keys, values):
    if values is None: return dict()
    return dict((keys[i], values.group(i+1)) for i in range(0, len(keys)))

keys = ["order_id"]
print(append_key_value(keys, m))


