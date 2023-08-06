import couchdb

class Manage:
    def __init__(self, realtime_db, user=None, password=None, server='127.0.0.1', port=5984):
        self.server = server
        self.port = port
        self.__realtimedb_name = realtime_db
        self.user = user
        self.password = password

    @property
    def realtime_db(self):
        if not self.user:
            couch = couchdb.Server('http://%s:%s/' % (self.server, self.port))
        else:
            couch = couchdb.Server('http://%s:%s@%s:%s/' % (self.user, self.password, self.server, self.port))
        return couch[self.__realtimedb_name]