import configparser
import logging
import multiprocessing
import re

import requests

from base import DummyGate


logger = multiprocessing.get_logger()
logger.setLevel(logging.INFO)


class HttpGate(DummyGate):
    def __init__(self, cfg: configparser.ConfigParser, section_name: str):
        super().__init__(cfg, section_name)
        self.base_url = cfg.get(section_name, 'url')
        global logger
        log_level = cfg.get('General', 'logLevel')
        if log_level:
            logger.setLevel(log_level)

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
            url = url.replace("{{{0}}}".format(p), str(msg.attributes[p]))

        # clean up unfilled parameters
        url = re.sub(r"[&?][^=]+={[^}]+}", "", url)
        try:
            logger.debug("get: %s", url)
            response = requests.get(url, timeout=5)
            logger.debug("response: %d: %s", response.status_code, response.content)

        except Exception as ex:
            logger.error('Cannot send data to: s', url,  exc_info=1)
