import time
import serial
import struct
import logging
from rhserial import RHSerial
 
def setup_custom_logger(name):
    formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    return logger

LOG = setup_custom_logger('sat_radio')
LOG.setLevel(logging.DEBUG)


class SatRadio(object):
    BROADCAST = 0xFF
 
    def __init__(self, port, address, callsign, baud_rate=38400, callback=None):
        self.port = port
        self.baud_rate = baud_rate
        self.serial_port = None
        self.radio = None
        self.frame_count = 1
        self.telem_index = 1
        self.address = address
        self.callsign = callsign
        self.user_callback = callback
        self.start()

    # No TX callbacks available

    def _rx_callback(self, packet):
        # Could do something here, I dunno.
        pass

 
    def _callback(self, data):
        try:
            self._rx_callback(data)
            if self.user_callback:
                self.user_callback(data)
        except Exception, e:
            print "Exception in data _callback: %s" % e
 
    def _construct_telemetry(self, 
        callsign, index, hhmmss, 
        lat_dec_deg, lon_dec_deg,
        lat_dil, alt,
        temp1, temp2,
        pressure):

        telem_str = "T|%s|%05d" % (callsign, index)
        # Time
        telem_str += hhmmss.strftime("|%H%M%S") if hhmmss else "|      "
        # GPS stuff
        telem_str += "|%c" % ("N" if lat_dec_deg > 0 else "S") if lat_dec_deg else "| "
        telem_str += "|%08.05f" % abs(lat_dec_deg) if lat_dec_deg else "|        "
        telem_str += "|%c" % ("E" if lon_dec_deg > 0 else "W") if lon_dec_deg else "| "
        telem_str += "|%09.05f" % abs(lon_dec_deg) if lon_dec_deg else "|         "
        telem_str += "|%05.02f" % lat_dil if lat_dil else "|     "
        telem_str += "|%08.02f" % alt if alt else "|        "
        # Temperatures
        telem_str += "|%+08.03f" % temp1 if temp1 else "|        "
        telem_str += "|%+08.03f" % temp2 if temp2 else "|        "
        # Pressure
        telem_str += "|%09.02f" % pressure if pressure else "|       "
        return telem_str
 
    def _encode_data(self, data):
        return b'%s' % data
 
    def start(self):
        self.serial_port = serial.Serial(self.port, self.baud_rate)
        self.radio = RHSerial(self.serial_port, address=self.address, callback=self._callback)
        self.radio.start()
 
    def stop(self):
        self.radio.stop()
        self.serial_port.close()
 
    def send_packet(self, data, address=0xFF):
        LOG.debug("Sending: %s" % data)
        frame_id = self.frame_count# struct.pack("B", self.frame_count)
        # Then try and transmit the packet
        self.radio.send(self._encode_data(data), to = address, id = frame_id)
        self.frame_count = ((self.frame_count + 1) % 250)

        return frame_id
 
    def send_telem(self, hhmmss, 
        lat_dec_deg, lon_dec_deg,
        lat_dil, alt,
        temp1, temp2,
        pressure):
        data = self._construct_telemetry(
            self.callsign.ljust(8)[:8], 
            self.telem_index, hhmmss, 
            lat_dec_deg, lon_dec_deg,
            lat_dil, alt,
            temp1, temp2,
            pressure
        )
        self.telem_index += 1
        return self.send_packet(data)
 
    def send_data(self, data):
        return self.send_packet(data)
