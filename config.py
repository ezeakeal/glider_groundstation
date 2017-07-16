# Get the config
import os
import ConfigParser

base_dir = os.path.dirname(__file__)
conf_path = os.path.join(base_dir, "groundstation_conf.ini")

groundstation_config = ConfigParser.ConfigParser()
groundstation_config.read(conf_path)
