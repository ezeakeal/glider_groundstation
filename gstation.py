#!/usr/bin/python
##############################################
#
# Glider GroundStation Software
# For use with launch of GliderV3:
#   Daniel Vagg 2017
#
##############################################
import os
import sys
import logging
import logging.config

##########################################
# Configure logging
base_dir = os.path.dirname(__file__)
conf_path = os.path.join(base_dir, "groundstation_conf.ini")
logging.config.fileConfig(conf_path)

LOG = logging.getLogger("groundstation")
##########################################

import tornado.web
import tornado.ioloop
import tornado.websocket
import tornado.httpserver

from request_handlers import *
from config import groundstation_config
from groundstation_radio import GroundRadio

GPIO = None
try:
    import RPi.GPIO as GPIO
except:
    print "Exception importing RPIGPIO"

#####################################
# GLOBALS
#####################################
LED_POWER = groundstation_config.getint("led", "on")
RemoteServerURL = "http://tracker.danvagg.space/"

#####################################
# WEB SERVER
#####################################
class Application(tornado.web.Application):
    radio = None
    socket_list = []

    def __init__(self):
        dirname = os.path.dirname(__file__)

        settings = {
            "template_path": os.path.join(dirname, 'templates'),
            "static_path": os.path.join(dirname, 'static'),
            "debug": True,
        }
        handlers = [
            (r"/", MainHandler),
            (r"/map", MapHandler),
            (r"/basic", BasicHandler),
            (r"/push_data", PushedDataHandler),
            (r'/(favicon.ico)', tornado.web.StaticFileHandler, {"path": ""}),
            (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': settings['static_path']}),
            (r"/getTelem", TelemHandler),
            (r"/getTelemSocket", TelemHandlerSocket),
            (r"/getPredict", PredictHandler),
            (r"/getPredictLand", PredictLandHandler),
            (r"/postCommand", CommandHandler),
        ]
        tornado.web.Application.__init__(self, handlers, **settings)

    def shut_down(self):
        LOG.info("Shutting down")
        if self.radio:
            self.radio.stop()

def runWebServer(port):
    application = Application()
    application.radio = GroundRadio(application)
    application.radio.start()
    http_server = tornado.httpserver.HTTPServer(application)
    print "GO TO: http://localhost:%s/" % port
    http_server.listen(port)
    try:
        tornado.ioloop.IOLoop.instance().start()
    except:
        application.shut_down()
    finally:
        if GPIO:
            GPIO.output(LED_POWER, False)  ## Turn on GPIO pin 7


#####################################
# MAIN
#####################################
def main():
    # Configure the GPIO if it imported
    if GPIO:
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup([LED_POWER], GPIO.OUT)
        GPIO.output(LED_POWER, GPIO.HIGH)

    server_port = groundstation_config.get("server", "port")
    runWebServer(server_port)
    sys.exit(0)


if __name__ == "__main__":
    main()
