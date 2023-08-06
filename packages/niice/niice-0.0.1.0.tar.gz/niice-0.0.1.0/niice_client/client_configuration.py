import socket
from pytz import timezone
import yaml
from niice_client.basic_configuration import BasicConfiguration

DEFAULT_CLIENT_CONFIG_PATH = "/etc/niice/client.yaml"

def client_configuration_from(config_file=DEFAULT_CLIENT_CONFIG_PATH):
    tz_name = "default"
    client_id = "default"
    rabbitmq_host = "127.0.0.1"
    rabbitmq_port = 5672
    rabbitmq_queue = "niice_realtime"
    rabbitmq_user = "guest"
    rabbitmq_password = "guest"

    try:
        with open(config_file, 'r') as f:
            config = yaml.load(f)

        #configuring timezone
        if config.has_key('timezone'):
            tz_name = config['timezone']

        #configuring timezone
        if config.has_key('client_id'):
            client_id = config['client_id']

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

    if client_id == "default":
        client_id = socket.gethostname()

    c = ClientConfiguration(rabbitmq_host, rabbitmq_port, rabbitmq_queue, rabbitmq_user, rabbitmq_password, server_id=client_id,
        tz=tz)
    return c

class ClientConfiguration(BasicConfiguration):
    def __init__(self, rabbitmq_host, rabbitmq_port, rabbitmq_queue, rabbitmq_user, rabbitmq_password, server_id=None,
                 tz=None):
        BasicConfiguration.__init__(self, rabbitmq_host, rabbitmq_port, rabbitmq_queue, rabbitmq_user,
            rabbitmq_password, tz=tz)
        self.server_id = server_id