import configparser
import os
import subprocess
from builtins import exit

import pkg_resources


def create_config(path):
    config = configparser.ConfigParser()
    config.add_section("DummyGate")
    config.set("DummyGate", "host", "0.0.0.0")
    config.set("DummyGate", "port", "5009")
    config.set("DummyGate", "protocol", "base:ProtocolBase")
    config.set("DummyGate", "gate", "base:DummyGate")

    config.add_section("WatchGate")
    config.set("WatchGate", "host", "0.0.0.0")
    config.set("WatchGate", "port", "5010")
    config.set("WatchGate", "protocol", "watch_protocol:WatchProtocol")
    config.set("WatchGate", "gate", "http_gate:HttpGate")
    config.set("WatchGate", "url", "https://nextcloud.local/apps/phonetrack/logGet/YOUR_SESSION_TOKEN/{id}?lat={latitude}&lon={longitude}&alt={altitude}&acc={accuracy}&bat={battery_percent}&sat={satellites}&speed={speed_kmh}&bearing={direction}&timestamp={timestamp}")

    with open(path, "w") as config_file:
        config.write(config_file)


def get_config(path):
    if not os.path.exists(path):
        # create_config(path)
        print(f"Config file '{path}' does not exist.")
        exit(-3)

    config = configparser.ConfigParser()
    config.read(path)
    return config


def get_gate_sections(path):
    config = get_config(path)
    result = []
    for section in iter(config.sections()):
        if section[-4:] == 'Gate':
            result.append(section)
    return result


def create_daemon():
    data_path = pkg_resources.resource_filename('gps2nextcloud', 'data/')
    service_file = os.path.join(data_path, "gps2nextcloud.service")
    dest_file = '/etc/systemd/system/gps2nextcloud.service'
    this_dir, this_filename = os.path.split(__file__)
    daemon_file = os.path.join(this_dir, "server.py")
    with open(service_file, "r") as src:
        with open(dest_file, "w") as dest:
            for line in src:
                dest.write(line.replace('{DAEMON_FILE}', daemon_file))
    print("Created systemd service file '%s'", dest_file)
    subprocess.run(["systemctl", "daemon-reload"])
    if not os.path.exists("/etc/gps2nextcloud"):
        os.makedirs("/etc/gps2nextcloud")
    create_config("/etc/gps2nextcloud/gps2nextcloud.ini")
    print("Created initial config file '/etc/gps2nextcloud/gps2nextcloud.ini'")
    print("Please check and edit it.")
    print("You need to change server address and 'YOUR_SESSION_TOKEN' to real token value from Nextcloud PhoneTrace application.")
    print("After that you can run daemon:")
    print(" systemctl start gps2nextcloud\n")
    print("To enable autostart of daemon:")
    print(" systemctl enable gps2nextcloud")
