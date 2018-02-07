class TransactionUpdateHistory:
    actor = None
    update_unix_timestamp = None
    action_code = None

    def __init__(self, actor, update_unix_timestamp, action_code, json_object=None):
        if json_object is not None and TransactionUpdateHistory.validate_json_object_schema(json_object):
            self.from_json_object(json_object)
        else:
            self.actor = actor
            self.update_unix_timestamp = update_unix_timestamp
            self.action_code = action_code

    def from_json_object(self, json_object):
        self.actor = json_object['actor']
        self.update_unix_timestamp = json_object['update_unix_timestamp']
        self.action_code = json_object['action_code']

    @staticmethod
    def validate_json_object_schema(json_object):
        if ['actor'] not in json_object or not json_object['actor']:
            return False
        if ['update_unix_timestamp'] not in json_object or not json_object['update_unix_timestamp']:
            return False
        if ['action_code'] not in json_object or not json_object['action_code']:
            return False
        return True


