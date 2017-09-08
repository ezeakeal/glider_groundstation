import json
import logging

import time

import requests

GPIO = None
try:
    import RPi.GPIO as GPIO
except:
    print "Exception importing RPIGPIO"


from sat_radio import SatRadio
from config import groundstation_config
from packet_handlers import TelemetryHandler, ImageHandler, DataHandler

LOG = logging.getLogger("groundstation.%s" % __name__)

class GroundRadio(SatRadio):
    BROADCAST = 0xFF
    raw_dump = groundstation_config.get("output", "raw_dump")
    telem_dump = groundstation_config.get("output", "telemetry_dump")
    led_tx = groundstation_config.getint("led", "tx")
    led_rx = groundstation_config.getint("led", "rx")

    def __init__(self, application):
        self.application = application

        self.telemetry_handler = TelemetryHandler()
        self.image_handler = ImageHandler()
        self.data_handler = DataHandler()

        self.raw_dump_file =  open(self.raw_dump, "a")
        self.telem_dump_file = open(self.telem_dump, "a")

        self.remote_groundstation_push_url = groundstation_config.get("remote", "server_url") + \
                                             groundstation_config.get("remote", "server_push")

        if GPIO:
            for led_ID in [self.led_tx, self.led_rx]:
                GPIO.setup([led_ID], GPIO.OUT)

        if groundstation_config.getboolean("radio", "enabled"):
            super(GroundRadio, self).__init__(
                groundstation_config.get("radio", "device_path"),
                int(groundstation_config.get("radio", "address"), 16),
                groundstation_config.get("radio", "callsign"),
                groundstation_config.getint("radio", "baud_rate"),
                self.packet_handler
            )

    ################################
    # The Callback!
    # This is called when data is received
    ################################
    def packet_handler(self, packet):
        try:
            self.raw_dump_file.write("%s\n" % packet)
            self.parse_packet(packet)
            self.upload_packet(packet)
        except:
            LOG.exception("Error parsing data")

    def parse_packet(self, data):
        source = data['from']
        data_packet = data['message']
        packet_signal = data['rssi']
        time_received = int(time.time())
        LOG.debug("Parsing packet data: %s" % data_packet)

        data_parts = str(data_packet).split("|")
        packet_type = data_parts[0]
        packet_data = data_parts[1:]
        self.push_data(source, packet_type, packet_data, time_received)
        self.push_data_client()
        self.handle_parsed_packet(source, packet_type, packet_data, packet_signal, time_received)

    def upload_packet(self, data):
        """Upload all packets to remote server to be parsed publicly"""
        requests.post(self.remote_groundstation_push_url, data=data)

    def handle_parsed_packet(self, source, packet_type, packet_data, packet_signal, time_received):
        if GPIO:
            GPIO.output(self.led_rx, GPIO.HIGH)
        if packet_type == "T":
            self.telemetry_handler.parse(source, packet_data, packet_signal, time_received)
        if packet_type == "I":
            self.image_handler.parse(source, packet_data, packet_signal, time_received)
        if packet_type == "D":
            self.data_handler.parse(source, packet_data, packet_signal, time_received)
        if GPIO:
            GPIO.output(self.led_rx, GPIO.LOW)

    def send_packet_led(self, *args, **kwargs):
        if GPIO:
            GPIO.output(self.led_tx, GPIO.HIGH)
        val = self.send_packet(*args, **kwargs)
        if GPIO:
            GPIO.output(self.led_rx, GPIO.LOW)
        return val

    def push_data_client(self):
        data_dictionary = {}
        all_data = self.telemetry_handler.get_all_dict()
        data_dictionary.update(all_data.get("glider", {}))
        data_dictionary.update({"all_data": all_data})
        data_dictionary.update(self.image_handler.get_dict())
        data_dictionary.update(self.data_handler.get_dict())
        for socket in self.application.socket_list:
            socket.write_message(data_dictionary)

    def get_data(self):
        data_dictionary = TelemetryHandler.get_all_dict()
        return data_dictionary
