import json
import logging

import time

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

        if GPIO:
            for led_ID in [self.led_tx, self.led_rx]:
                GPIO.setup([led_ID], GPIO.OUT)

        super(GroundRadio, self).__init__(
            groundstation_config.get("radio", "device_path"),
            int(groundstation_config.get("radio", "address"), 16),
            groundstation_config.get("radio", "callsign"),
            groundstation_config.getint("radio", "baud_rate"),
            self.packet_handler
        )

    def packet_handler(self, packet):
        try:
            self.raw_dump_file.write("%s\n" % packet)
            self.parse_packet(packet)
        except:
            LOG.exception("Error parsing data")

    def parse_packet(self, data):
        source = data['from']
        data_packet = data['message']
        time_received = int(time.time())
        LOG.debug("Parsing packet data: %s" % data_packet)

        data_parts = str(data_packet).split("|")
        packet_type = data_parts[0]
        packet_data = data_parts[1:]
        self.push_data(source, packet_type, packet_data, time_received)
        self.push_data_server()
        self.handle_parsed_packet(source, packet_type, packet_data, time_received)

    def handle_parsed_packet(self, source, packet_type, packet_data, time_received):
        if GPIO:
            GPIO.output(self.led_rx, GPIO.HIGH)
        if packet_type == "T":
            self.telemetry_handler.parse(source, packet_data, time_received)
        if packet_type == "I":
            self.image_handler.parse(source, packet_data, time_received)
        if packet_type == "D":
            self.data_handler.parse(source, packet_data, time_received)
        if GPIO:
            GPIO.output(self.led_rx, GPIO.LOW)

    def send_packet_led(self, *args, **kwargs):
        if GPIO:
            GPIO.output(self.led_tx, GPIO.HIGH)
        val = self.send_packet(*args, **kwargs)
        if GPIO:
            GPIO.output(self.led_rx, GPIO.LOW)
        return val

    def push_data(self, source, packet_type, packet_data, time_received):
        if packet_type == "I":
            return
        send_packet = {
            "secret_sauce": "captainmorgan",
            "source": source,
            "packet_type": packet_type,
            "packet_data": packet_data,
            "time_received": time_received
        }
        json.dump(send_packet, self.telem_dump_file)

    def push_data_server(self):
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
