import logging
import multiprocessing

import pytz as pytz
from builtins import len, int
from datetime import datetime

from gps2nextcloud import base

logger = multiprocessing.get_logger()
logger.setLevel(logging.INFO)


class H02Protocol(base.ProtocolBase):
    def __init__(self, selector, sock, addr, gate):
        base.ProtocolBase.__init__(self, selector, sock, addr, gate)
        self.last_location = None
        self.serial_number = None

    def process_message(self):
        while self._recv_buffer:
            start = self._recv_buffer.find(b'*')
            if start == 0:
                end = self._recv_buffer.find(b'#')
                if end == -1:
                    return

                end += 1
                msg = self._recv_buffer[:end].decode('utf8')
                self._recv_buffer = self._recv_buffer[end:]
                self.parse_ascii_message(msg)
                continue

            start = self._recv_buffer.find(b'$')
            if start == 0:
                if len(self._recv_buffer) < 32:
                    return

                bin_msg = self._recv_buffer[:32]
                self._recv_buffer = self._recv_buffer[32:]
                self.serial_number = self.parse_bin_message(bin_msg, '')
                continue

            start = self._recv_buffer.find(b'X')
            if start == 0:
                if len(self._recv_buffer) < 32:
                    return
                bin_msg = self._recv_buffer[:32]
                self._recv_buffer = self._recv_buffer[32:]
                self.parse_bin_message(bin_msg, self.serial_number)
                continue

            self._recv_buffer = None
            self.send_and_terminate(b'wrong format')

    def parse_ascii_message(self, msg):
        logger.debug("parsing '%s'", msg)
        splits = msg.split(sep=",", maxsplit=15)
        supplier = splits[0][1:]
        imei = splits[1]
        version = splits[2]
        msg = H02Message(supplier, imei)

        if version == 'V1':
            if len(splits) < 13:
                logger.debug("Only '%d' fields for 'V1'", len(splits))
                return
            msg.parse_v1(splits)
        elif version == 'VP1':
            if len(splits) < 12:
                logger.debug("Only '%d' fields for 'VP1'", len(splits))
                return
            msg.parse_vp1(splits)
        else:
            logger.debug("Unknown version '%s'", version)
            return

        if msg.is_parsed:
            if msg.location:
                self.last_location = msg.location
            else:
                msg.location = self.last_location
            self.register_message(msg)
        else:
            self.send_and_terminate(None)
            return
        buffer = msg.build_reply()
        if not (buffer is None):
            self.reply(buffer)

    def parse_bin_message(self, buf, imei):
        logger.debug("parsing '%s'", ":".join("{:02x}".format(c) for c in buf))
        msg = H02Message('--', imei)
        if len(imei)<1:
            imei = msg.parse_bin(buf)
        else:
            msg.parse_x(buf, imei)

        if msg.is_parsed:
            if msg.location:
                self.last_location = msg.location
            else:
                msg.location = self.last_location
            self.register_message(msg)
        else:
            self.send_and_terminate(None)
            return None
        buffer = msg.build_reply()
        if not (buffer is None):
            self.reply(buffer)
        return imei


class H02Message(base.TrackerMessage):
    def __init__(self, company, client_id):
        base.TrackerMessage.__init__(self, client_id)
        self.attributes["company"] = company
        self._is_parsed = False

    def parse_v1(self, splits):
        self._is_parsed = False
        self.location = base.Location()
        self.location.timestamp = datetime.strptime(f"{splits[11]} {splits[3]}", "%d%m%y %H%M%S") \
            .replace(tzinfo=pytz.utc)
        self.location.locked_position = splits[4] == 'A'
        latitude = splits[5]
        self.location.latitude = float(latitude[:2]) + (float(latitude[2:])/60)
        if splits[6] == 'S':
            self.location.latitude *= -1
        longitude = splits[7]
        self.location.longitude =  float(longitude[:3]) + (float(longitude[3:])/60)
        if splits[8] == 'W':
            self.location.longitude *= -1
        knots = splits[9]
        if len(knots) >0:
            self.location.speed_ms = float(knots) * 0.5144
        else:
            self.location.speed_ms = 0
        direction = splits[10]
        if len(direction) > 0:
            self.location.direction = float(direction)
        else:
            self.location.direction = 0
        # vehicleStatus = splits[12]
        if len(splits) > 13:
            self.attributes["battery_percent"] = int(splits[13])
        self._is_parsed = True

    def parse_vp1(self, splits):
        self._is_parsed = False
        source = splits[3]
        if source != 'A' and source != 'B':
            logger.debug("Unsupported source '%s' for 'VP1'", source)
            return

        self.location = base.Location()
        self.location.timestamp = datetime.utcnow()
        self.location.locked_position = True
        latitude = splits[4]
        self.location.latitude = float(latitude[:2]) + (float(latitude[2:]) / 60)
        if splits[5] == 'S':
            self.location.latitude *= -1
        longitude = splits[6]
        self.location.longitude = float(longitude[:3]) + (float(longitude[3:]) / 60)
        if splits[7] == 'W':
            self.location.longitude *= -1
        knots = splits[8]
        if len(knots) > 0:
            self.location.speed_ms = float(knots) * 0.5144
        else:
            self.location.speed_ms = 0
        direction = splits[9]
        if len(direction) > 0:
            self.location.direction = float(direction)
        else:
            self.location.direction = 0
        # vehicleStatus = splits[11]
        if len(splits) > 12:
            self.attributes["battery_percent"] = int(splits[12])
        self._is_parsed = True

    def parse_bin(self, buf):
        self.id = "".join("{:02x}".format(c) for c in buf[1:6])
        time = "".join("{:02x}".format(c) for c in buf[6:9])
        date = "".join("{:02x}".format(c) for c in buf[9:12])
        self.location = base.Location()
        self.location.timestamp = datetime.strptime(f"{date} {time}", "%d%m%y %H%M%S") \
            .replace(tzinfo=pytz.utc)
        latitude = "".join("{:02x}".format(c) for c in buf[12:16])
        self.location.latitude = float(latitude[:2]) + (float(latitude[2:4] + '.' + latitude[4:]) / 60)
        longitude = "".join("{:02x}".format(c) for c in buf[17:22])
        self.location.longitude = float(longitude[:3]) + (float(longitude[3:5] + '.' + latitude[5:9]) / 60)
        bits = int(longitude[9], 16)
        self.location.locked_position = bits & 0b0010
        if not bits & 0b0100:
            self.location.latitude *= -1
        if not bits & 0b1000:
            self.location.longitude *= -1
        speed_direction = "".join("{:02x}".format(c) for c in buf[22:25])
        knots = speed_direction[:3]
        self.location.speed_ms = float(knots) * 0.5144
        direction = speed_direction[3:]
        self.location.direction = float(direction)
        self._is_parsed = True
        return self.id

    def parse_x(self, buf, imei):
        self.id = imei
        # mileage =  "".join("{:02x}".format(c) for c in buf[1:6])
        time = "".join("{:02x}".format(c) for c in buf[6:9])
        date = "".join("{:02x}".format(c) for c in buf[9:12])
        self.location = base.Location()
        self.location.timestamp = datetime.strptime(f"{date} {time}", "%d%m%y %H%M%S") \
            .replace(tzinfo=pytz.utc)
        latitude = "".join("{:02x}".format(c) for c in buf[12:16])
        self.location.latitude = float(latitude[:2]) + (float(latitude[2:3] + '.' + latitude[4:]) / 60)
        longitude = "".join("{:02x}".format(c) for c in buf[17:22])
        self.location.longitude = float(longitude[:3]) + (float(longitude[3:4] + '.' + latitude[5:8]) / 60)
        bits = int(latitude[9], 16)
        self.location.locked_position = bits & 0b0010
        if not bits & 0b0100:
            self.location.latitude *= -1
        if not bits & 0b1000:
            self.location.longitude *= -1
        speed_direction = "".join("{:02x}".format(c) for c in buf[22:25])
        knots = speed_direction[:2]
        self.location.speed_ms = float(knots) * 0.5144
        direction = speed_direction[2:]
        self.location.direction = float(direction)
        self._is_parsed = True
        return self.id


    @property
    def is_parsed(self):
        return self._is_parsed

    def build_reply(self):
        return None

