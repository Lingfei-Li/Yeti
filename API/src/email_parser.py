import html2text
import re


# Venmo Naming Conventions:
# First/Last Name - Letters Only
# Username - letters, numbers, (-), 5-16 in length
# payment ID seems to be 19 in length - Need to verify

def parse(email_html_format):
    transaction_information = dict()

    h = html2text.HTML2Text()
    h.ignore_links = False
    h.body_width = 300
    email_md = h.handle(email_html_format)
    # print email_md

    # print email_html_format
    transaction_information.update(parse_payer_information(email_md)) # gather my_venmo_id, payer_venmo_id, payer_name, amount
    transaction_information.update(parse_time_amount_information(email_md)) # time, amount
    transaction_information.update(parse_comments((email_md)))
    transaction_information.update(parse_payment_id(email_md)) # payment_id

    print transaction_information

    return transaction_information

#TODO: Need to merge regex, since all of them are next to each other and merging all regex makes matching "comments" field more reliable
def parse_payer_information(email):
    try:
        name_id_matching_pattern = "\[([a-zA-Z\ ]+)\]\(https:\/\/venmo\.com\/([a-zA-Z\-0-9]{5,16})\)"
        action_matching_pattern = "(charged |paid )"
        name_id_regex = name_id_matching_pattern + action_matching_pattern + name_id_matching_pattern
        m = re.search(name_id_regex, email)

        print m.groups()
        keys = ["venmo_id_1", "venmo_name_1", "action", "venmo_id_2", "venmo_name_2"]
        return append_key_value(keys, m)
    except AttributeError as e:
        print("error parsing payer info")
        print e
        # print email
        return dict()

#TODO: need to be more robust
def parse_time_amount_information(email):
    try:
        time_amount_regex = "!\[private\]\(https:\/\/s3\.amazonaws\.com\/venmo\/audience\/private\.png\) (\+|\\\-) \$([0-9]+\.[0-9]{2})"

        m = re.search(time_amount_regex, email)

        print m.groups()
        keys = ["operator", "amount"]
        return append_key_value(keys, m)
    except AttributeError as e:
        print("error parsing time amount info")
        print e
        # print email
        return dict()

#TODO: Fix Comment
def parse_comments(email):
    # try:
    #     name_id_matching_pattern = "\[[a-zA-Z\ ]+\]\(https:\/\/venmo\.com\/[a-zA-Z\-0-9]{5,16}\)"
    #     action_matching_pattern = "(?:charged |paid )"
    #     name_id_regex = name_id_matching_pattern + action_matching_pattern + name_id_matching_pattern
    #     empty_line = "\n"
    #     time_amount_regex = "\-\-\-\|\-\-\-  \n\| Transfer Date and Amount:  "
    #     comments_regex = name_id_regex + empty_line + "(\X+)" + time_amount_regex
    #     m = re.search(comments_regex, email)
    #
    #     print m.groups()
    #     keys = ["venmo_id_1", "venmo_name_1", "action", "venmo_id_2", "venmo_name_2"]
    #     return append_key_value(keys, m)
    # except AttributeError as e:
    #     print("error parsing comments")
    #     print e
    #     # print email
    #     return dict()
    return dict()

def parse_payment_id(email):
    try:
        payment_id_regex = "Payment ID: ([0-9]{19})"
        m = re.search(payment_id_regex, email)

        print m.groups()
        keys = ["payment_id"]
        return append_key_value(keys, m)
    except AttributeError as e:
        print("error parsing payment_id")
        print e
        # print email
        return dict()

def append_key_value(keys, values):
    return dict((keys[i], values.group(i+1)) for i in range(0, len(keys)))