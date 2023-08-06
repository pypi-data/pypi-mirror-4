__author__ = 'jcorbett'

import configparser
import sys
import logging

basic_configuration = """
[Slick]
url = http://localhost:8080/slickij

[Logging]
logfile = /var/log/narc.log
level = INFO
stdout = False
format = [{process:<6}|{asctime}|{levelname:<8}|{name}]: {message}
dateformat = %x %I:%M:%S %p
"""

def load_configuration(filepath):
    logger = logging.getLogger("narc.configuration.load_configuration")
    logger.debug("Loading configuration from file path {}", filepath)
    config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
    config.read_string(basic_configuration)
    files_read = config.read([filepath,])
    if len(files_read) is 0:
        logger.debug("Unable to read config file '{}', using defaults.", filepath)
    return config

def save_configuration(filepath, config):
    assert(isinstance(config, configparser.ConfigParser))
    logger = logging.getLogger("narc.configuration.save_configuration")
    logger.debug("Attempting to save configuration file {}.", filepath)
    try:
        with open(filepath, 'w') as configfile:
            config.write(configfile)
    except:
        logger.warn("Unable to write configuration file '{}': ", filepath, exc_info=sys.exc_info())
        raise

