from pytz import timezone
import yaml
from niice_client.basic_configuration import BasicConfiguration

DEFAULT_SERVER_CONFIG_PATH = "/etc/niice/server.yaml"

def server_configuration_from(config_file=DEFAULT_SERVER_CONFIG_PATH):
    tz_name = "default"

    rabbitmq_host = "127.0.0.1"
    rabbitmq_port = 5672
    rabbitmq_queue = "niice_realtime"
    rabbitmq_user = "guest"
    rabbitmq_password = "guest"

    couchdb_host = "127.0.0.1"
    couchdb_port = 5984
    couchdb_realtime_db = "niice_realtime"
    couchdb_historical_db = "niice_hisotrical"
    couchdb_user = None
    couchdb_password = None

    try:
        with open(config_file, 'r') as f:
            config = yaml.load(f)
        #configuring timezone
        if config.has_key('timezone'):
            tz_name = config['timezone']

        #configuring rabbitmq
        if 'rabbitmq' in config:
            rabbit = config['rabbitmq']
            if 'host' in rabbit:
                rabbitmq_host = rabbit['host']
            if 'port' in rabbit:
                rabbitmq_port = rabbit['port']
            if 'queue' in rabbit:
                rabbitmq_queue = rabbit['queue']
            if 'user' in rabbit:
                rabbitmq_user = rabbit['user']
            if 'password' in rabbit:
                rabbitmq_password = rabbit['password']

        #configuring couchdb
        if 'couch' in config:
            couch = config['couch']
            if 'host' in couch:
                couchdb_host = couch['host']
            if 'port' in couch:
                couchdb_port = couch['port']
            if 'realtime_db' in couch:
                couchdb_realtime_db = couch['realtime_db']
            if 'historical_db' in couch:
                couchdb_historical_db = couch['historical_db']
            if 'user' in couch:
                couchdb_user = couch['user']
            if 'password' in couch:
                couchdb_password = couch['password']

    except IOError:
        pass

    if tz_name == "default":
        try:
            with open("/etc/timezone", 'r') as f:
                data = f.read()
            tz_name = data.strip()
        except IOError:
            tz_name = "America/Los_Angeles"
    tz = timezone(tz_name)

    c = ServerConfiguration(
        rabbitmq_host,
        rabbitmq_port,
        rabbitmq_queue,
        rabbitmq_user,
        rabbitmq_password,
        couchdb_host,
        couchdb_port,
        couchdb_realtime_db,
        couchdb_historical_db,
        couchdb_user,
        couchdb_password,
        tz=tz)
    return c

class ServerConfiguration(BasicConfiguration):
    def __init__(self,
                 rabbitmq_host,
                 rabbitmq_port,
                 rabbitmq_queue,
                 rabbitmq_user,
                 rabbitmq_password,
                 couchdb_host,
                 couchdb_port,
                 realtime_db,
                 historical_db,
                 couchdb_user,
                 couchdb_password,
                 tz=None):
        BasicConfiguration.__init__(self, rabbitmq_host, rabbitmq_port, rabbitmq_queue, rabbitmq_user,
            rabbitmq_password, tz=tz)
        self.couchdb_host = couchdb_host
        self.couchdb_port = couchdb_port
        self.couchdb_user = couchdb_user
        self.couchdb_password = couchdb_password
        self.realtime_db = realtime_db
        self.historical_db = historical_db
