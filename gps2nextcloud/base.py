import configparser
import datetime
import logging
import multiprocessing
import selectors
import socket

# logger = logging.getLogger("gate_base")
logger = multiprocessing.get_logger()
logger.setLevel(logging.INFO)


class TrackerMessage:
    def __init__(self, client_id):
        self.id = client_id
        self.location = None
        self.attributes = {}
        self.forward = True

    def print_me(self):
        print(f"client: {self.id}")
        print("location:")
        print(self.location)
        print(self.attributes)

    def __str__(self):
        return f"client_id: {self.id} {self.location} {self.attributes}"


class DummyGate:
    def __init__(self, cfg: configparser.ConfigParser, section_name: str):
        self._cfg = cfg
        self._cfg_section_name = section_name

    def send_message(self, msg: TrackerMessage):
        """
        You need to implement send_message method.
        Base DummyGate does simply logging of received message
        """
        logger.info(msg)


class ProtocolBase:
    def __init__(self, selector: selectors.BaseSelector, sock: socket.socket, addr, gate: DummyGate):
        self.selector = selector
        self.sock = sock
        self.addr = addr
        self._recv_buffer = b""
        self._send_buffer = b""
        self.request = None
        self.response_created = False
        self._keep_connection = True
        self._gate = gate

    def _set_selector_events_mask(self, mode):
        """Set selector to listen for events: mode is 'r', 'w', or 'rw'."""
        if mode == "r":
            events = selectors.EVENT_READ
        elif mode == "w":
            events = selectors.EVENT_WRITE
        elif mode == "rw":
            events = selectors.EVENT_READ | selectors.EVENT_WRITE
        else:
            raise ValueError(f"Invalid events mask mode {repr(mode)}.")
        self.selector.modify(self.sock, events, data=self)

    def _read(self):
        try:
            # Should be ready to read
            data = self.sock.recv(4096)
        except io.BlockingIOError:
            # Resource temporarily unavailable (errno EWOULDBLOCK)
            pass
        else:
            if data:
                self._recv_buffer += data
            else:
                raise RuntimeError("Peer closed.")

    def _write(self):
        if self._send_buffer:
            print("sending", repr(self._send_buffer), "to", self.addr)
            try:
                # Should be ready to write
                sent = self.sock.send(self._send_buffer)
            except io.BlockingIOError:
                # Resource temporarily unavailable (errno EWOULDBLOCK)
                pass
            else:
                self._send_buffer = self._send_buffer[sent:]
                if not self._keep_connection and sent and not self._send_buffer:
                    self.close()
        elif not self._keep_connection:
            self.close()

    def send_and_terminate(self, buffer):
        self._send_buffer = buffer
        self._keep_connection = False
        self._set_selector_events_mask('w')

    def reply(self, buffer):
        self._send_buffer += buffer
        self._set_selector_events_mask('rw')

    def process_events(self, mask):
        if mask & selectors.EVENT_READ:
            self.read()
        if mask & selectors.EVENT_WRITE:
            self.write()

    def read(self):
        self._read()
        self.process_message()

    def write(self):
        # if self.request:
        #     if not self.response_created:
        #         self.create_response()

        self._write()

    def close(self):
        print("closing connection to", self.addr)
        try:
            self.selector.unregister(self.sock)
        except Exception as e:
            print(
                f"error: selector.unregister() exception for",
                f"{self.addr}: {repr(e)}",
            )

        try:
            self.sock.close()
        except OSError as e:
            print(
                f"error: socket.close() exception for",
                f"{self.addr}: {repr(e)}",
            )
        finally:
            # Delete reference to socket object for garbage collection
            self.sock = None

    def process_message(self):
        # need to implement this method for real protocol
        # mark all data as processed
        return len(self._recv_buffer)

    def register_message(self, msg):
        if msg.forward:
            self._gate.send_message(msg)


class GsmBaseStation:
    def __init__(self, mcc, mnc, lac, cell_id, signal):
        self.mcc = mcc
        self.mnc = mnc
        self.lac = lac
        self.cell_id = cell_id
        self.signal = signal


class Location:
    def __init__(self):
        self.timestamp = datetime.datetime.utcnow()
        self.locked_position = False
        self.latitude = 0.0
        self.longitude = 0.0
        self.speed_ms = 0
        self.direction = 0.
        self.altitude = 0.0
        self.satellites = 0
        self.gsm_signal_percent = 0
        self.gsm_station_numbers = 0
        self.gsm_time_delay = 0
        self.gsm_stations = []

    def __str__(self):
        response = f"{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')} Fix:{self.locked_position} Lat:{self.latitude} Lon:{self.longitude}\n"\
               + f"Alt:{self.altitude} Speed:{self.speed_ms}m/s Dir:{self.direction}\n" \
               + f"Satellites:{self.satellites} GSM signal:{self.gsm_signal_percent}%\n"
        n = 1
        for b in iter(self.gsm_stations):
            response += f"Base{n}: MCC:{b.mcc} MNC:{b.mnc} {b.lac}.{b.cell_id} power:{b.signal}\n"
            n += 1
        return response
