import configparser

import requests

from gps2nextcloud.base import DummyGate


class HttpGate(DummyGate):
    def __init__(self, cfg: configparser.ConfigParser, section_name: str):
        super().__init__(cfg, section_name)
        self.base_url = cfg.get(section_name, 'url')

    def send_message(self, msg):
        url = self.base_url\
            .replace('{id}', msg.id)
        if msg.location:
            url = url.replace('{longitude}', str(msg.location.longitude)) \
                .replace('{latitude}', str(msg.location.latitude)) \
                .replace('{altitude}', str(msg.location.altitude)) \
                .replace('{speed_ms}', str(msg.location.speed_ms)) \
                .replace('{speed_kmh}', str(msg.location.speed_ms*3600/1000)) \
                .replace('{satellites}', str(msg.location.satellites)) \
                .replace('{direction}', str(msg.location.direction)) \
                .replace('{timestamp}', str(msg.location.timestamp.timestamp()))
        for p in iter(msg.attributes):
            url = url.replace(f"{{{p}}}", str(msg.attributes[p]))
        try:
            response = requests.get(url, timeout=5)
        except Exception as ex:
            print('Cannot send data to:', url, ex)
