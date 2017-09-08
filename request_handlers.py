#!/usr/bin/python
##############################################
#
# Glider GroundStation Software
# For use with launch of GliderV3:
#   Daniel Vagg 2017
#
##############################################
import json
import logging
import datetime
import requests
import tornado

from config import groundstation_config
from packet_handlers import TelemetryHandler

LOG = logging.getLogger('groundstation.%s' % __name__)

class MainHandler(tornado.web.RequestHandler):

    def get(self):
        self.render("index.html")


class MapHandler(tornado.web.RequestHandler):

    def get(self):
        self.render("map.html")


class BasicHandler(tornado.web.RequestHandler):

    def get(self):
        data = TelemetryHandler.get_all_dict()
        self.render("basic.html", data=data)


class TelemHandler(tornado.web.RequestHandler):

    def get(self):
        self.write(json.dumps(TelemetryHandler.get_all_dict()))


class TelemHandlerSocket(tornado.websocket.WebSocketHandler):

    def open(self):
        print "WebSocket opened"
        self.application.socket_list.append(self)

    def on_close(self):
        print "WebSocket closed"
        self.application.socket_list.remove(self)


class PredictHandler(tornado.web.RequestHandler):
    def post(self):
        my_data = self.request.arguments
        LOG.debug("Received my_data: %s" % my_data)
        requrl="http://predict.habhub.org/ajax.php?action=submitForm"
        now = datetime.now()
        payload = {
            "launchsite": "Other",
            "lat": my_data['lat'][0],
            "lon": my_data['lon'][0],
            "initial_alt": my_data['alt'][0],
            "hour": now.hour, "min": now.min, "second": now.second,
            "day": now.day, "month": now.month, "year": now.year,
            "ascent": 5,
            "burst": 24000,
            "drag": 5,
            "submit": "Run Prediction"
        }
        res = requests.post(requrl, data=payload)
        res.raise_for_status()
        predict_url = "http://predict.habhub.org/#!/uuid=%s" % res.json()['uuid']
        LOG.debug("Sending to %s" % predict_url)
        self.write(predict_url)


class PredictLandHandler(tornado.web.RequestHandler):
    def post(self):
        my_data = self.request.arguments
        LOG.debug("Received my_data: %s" % my_data)
        requrl="http://predict.habhub.org/ajax.php?action=submitForm"
        now = datetime.now()
        payload = {
            "launchsite": "Other",
            "lat": my_data['lat'][0],
            "lon": my_data['lon'][0],
            "initial_alt": my_data['alt'][0],
            "hour": now.hour, "min": now.min, "second": now.second,
            "day": now.day, "month": now.month, "year": now.year,
            "ascent": 5,
            "burst": my_data['alt'][0],
            "drag": 5,
            "submit": "Run Prediction"
        }
        res = requests.post(requrl, data=payload)
        res.raise_for_status()
        predict_url = "http://predict.habhub.org/#!/uuid=%s" % res.json()['uuid']
        LOG.debug("Sending to %s" % predict_url)
        self.write(predict_url)

class CommandHandler(tornado.web.RequestHandler):

    def post(self):
        pitch = self.get_argument('pitch', None)
        state = self.get_argument('select_state', None)
        severity = self.get_argument('severity', None)
        lon = self.get_argument('lon', None)
        lat = self.get_argument('lat', None)
        image = self.get_argument('image', None)

        if not self.application.radio:
            raise Exception("No radio available")

        if pitch:
            self.sendCommand_pitch(pitch)
        if state:
            self.sendCommand_state(state)
        if severity:
            self.sendCommand_severity(severity)
        if lat and lon:
            self.sendCommand_location(lat, lon)
        if image is not None:
            self.sendCommand_get_image(image)
        self.set_status(200)
        self.redirect('/')

    def sendCommand(self, command, dest_addr=None):
        if not dest_addr:
            dest_addr = int(groundstation_config.get("radio", "glider_address"), 16)
        LOG.debug("Sending command: '%s' to (%s)" % (command, dest_addr))
        command = "".join([chr(ord(c)) for c in command])  # YES ITS THE FUCKING SAME
        # But no.. it's not. Not if the string comes from the dropdown list in the
        # web page. Because even though the characters are what you'd expect.. they
        # arent the same. I compared and checked.. it's black magic.
        response = self.application.radio.send_packet_led("%s" % command, address=dest_addr)
        LOG.debug("Command response: %s" % (response))

    def sendCommand_pitch(self, pitch):
        return self.sendCommand("PA|%2.2f" % float(pitch))

    def sendCommand_state(self, state):
        return self.sendCommand("O|%s" % state)

    def sendCommand_severity(self, severity):
        return self.sendCommand("TS|%s" % severity)

    def sendCommand_location(self, lat, lon):
        return self.sendCommand("DEST|%s|%s" % (lat, lon))

    def sendCommand_get_image(self, image):
        return self.sendCommand("IMAGE|0")


class PushedDataHandler(tornado.web.RequestHandler):

    def post(self):
        LOG.debug("Received post_data: %s" % self.request.body)
        data = json.loads(self.request.body)
        if not self.application.radio:
            raise Exception("No radio available")
        else:
            self.application.radio.parse_packet(data)
        self.set_status(200)
        self.write(data)
