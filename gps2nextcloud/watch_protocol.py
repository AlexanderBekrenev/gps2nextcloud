import pytz as pytz
from builtins import len, int
from datetime import datetime

from gps2nextcloud import base


class WatchProtocol(base.ProtocolBase):
    def __init__(self, selector, sock, addr, gate, log_all_messages):
        base.ProtocolBase.__init__(self, selector, sock, addr, gate, log_all_messages)

    def process_message(self):
        while self._recv_buffer:
            start = self._recv_buffer.find(b'[')
            if start == -1:
                self._recv_buffer = None
                self.send_and_terminate(b'wrong format')

                return
            if start > 0:
                self._recv_buffer = self._recv_buffer[start:]
            end = self._recv_buffer.find(b']')
            if end == -1:
                return
            end += 1
            msg = self._recv_buffer[:end].decode('utf8')
            self._recv_buffer = self._recv_buffer[end:]
            self.parse_message(msg)

    def parse_message(self, msg):
        print("parsing", msg)
        splits = msg.split(sep="*", maxsplit=4)
        company = splits[0][1:]
        client_id = splits[1]
        content_len = splits[2]
        content = splits[3][:-1]
        l1 = len(content)
        l2 = int(content_len, base=16)
        if l1 != l2:
            self.send_and_terminate(f"wrong content length. real:{l1} reported:{l2}".encode('utf8'))
            return
        msg = WatchMessage(company, client_id, content)
        if msg.is_parsed:
            self.register_message(msg)
        else:
            self.send_and_terminate(None)
            return
        buffer = msg.build_reply()
        if not (buffer is None):
            self.reply(buffer)


class WatchMessage(base.TrackerMessage):
    def __init__(self, company, client_id, content):
        base.TrackerMessage.__init__(self, client_id)
        self.attributes["company"] = company
        self._content = content
        self._command = None
        self._is_parsed = False
        self.parse_content()

    def parse_content(self):
        self._is_parsed = False
        splits = self._content.split(sep=',')
        self._command = splits[0]
        if self._command == "LK":
            if 4 == len(splits):
                self.attributes["steps"] = int(splits[1])
                self.attributes["rollings"] = int(splits[2])
                self.attributes["battery_percent"] = int(splits[3])
            else:
                self.forward = True # don't forward simple ping-pong
            self._is_parsed = True
        elif self._command == "UD" or self._command == "UD2":
            # example UD,220414,134652,A,22.571707,N,113.8613968,E,0.1,0.0,100,7,60,90,1000,50,0000,4,1,460,0,9360,4082,131,9360,4092,148,9360,4091,143,9360,4153,141
            self.location = base.Location()
            self.location.timestamp = datetime.strptime(f"{splits[1]} {splits[2]}", "%d%m%y %H%M%S")\
                .replace(tzinfo=pytz.utc)
            self.location.locked_position = splits[3] == 'A'
            self.location.latitude = float(splits[4])
            if splits[5] == 'S':
                self.location.latitude *= -1
            self.location.longitude = float(splits[6])
            if splits[7] == 'W':
                self.location.longitude *= -1
            mph = float(splits[8])
            self.location.speed_ms = mph * 0.44704
            self.location.direction = float(splits[9])
            self.location.altitude = float(splits[10])
            self.location.satellites = int(splits[11])
            self.location.gsm_signal_percent = int(splits[12])
            self.attributes["battery_percent"] = int(splits[13])
            self.attributes["steps"] = int(splits[14])
            self.attributes["rollings"] = int(splits[15])
            self.attributes["statement"] = splits[16]  # TODO
            self.location.gsm_station_numbers = int(splits[17])
            self.location.gsm_time_delay = int(splits[18])
            mcc = int(splits[19])
            mnc = int(splits[20])
            index = 21
            while index +3 < len(splits):
                self.location.gsm_stations.append(base.GsmBaseStation(mcc, mnc,
                                                                      int(splits[index]),
                                                                      int(splits[index+1]),
                                                                      int(splits[index+2])))
                index += 3
            if index < len(splits):
                self.attributes["unknown1"] = splits[index]  # TODO
                index += 1
            if index < len(splits):
                self.attributes["accuracy"] = float(splits[index])  # accuracy?
                index += 1
            self._is_parsed = True
        else:
            print(f"Unknown command: {self._content}")
        self._content = None

    @property
    def is_parsed(self):
        return self._is_parsed

    def build_reply(self):
        if self._command is None and self._content is None:
            return None
        if self._content is None:
            self._content = self.build_reply_content()
            if self._content is None:
                return None
        buf = f"[{self.attributes['company']}*{self.id}*{len(self._content)}*{self._content}]"
        return buf.encode('utf8')

    def build_reply_content(self):
        if self._command is None:
            return None
        if self._command == "LK":
            return "LK"
        if self._command == "AL":
            return "AL"
        return None

