import pytz

class Event:
    def __init__(self, server_id, event_key, value, when):
        self.server_id = server_id
        self.event_key = event_key
        self.value = value
        self.when = int(when.astimezone(pytz.utc).strftime("%s"))
