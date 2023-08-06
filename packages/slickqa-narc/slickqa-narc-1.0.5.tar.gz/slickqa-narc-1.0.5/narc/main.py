"""
The main program for narc.  This contains both the daemon's main, and the control script main.
"""
__author__ = 'jcorbett'

import sys
import argparse
import logging
import traceback
import socket

from kombu import Producer
from kombu.utils import nested
import pkg_resources
from slickqa import SlickConnection, AMQPSystemConfiguration

from .log import initialize_logging
from . import configuration
from . import amqp


def validate_slick_connection(slick):
    assert(isinstance(slick, SlickConnection))
    logger = logging.getLogger("narc.main.validate_slick_connection")
    logger.debug("Attempting to connect to slick at url {}", slick.baseUrl)
    versioninfo = slick.version.findOne()
    logger.info("Connected to {} version {} at url {}", versioninfo.productName, versioninfo.versionString, slick.baseUrl)

def validate_amqp_connection(amqpcon):
    #assert(isinstance(amqpcon, amqp.AMQPConnection))
    pass

def setup(options):
    """This method gets everything ready.  It loads configuration, initializes logging, initializes the connection
    to slick and the amqp broker.

    Note that it does not validate the amqp connection, only sets up the configuration.
    """
    config = configuration.load_configuration(options.configpath)
    if options.stdout:
        config['Logging']['stdout'] = 'True'
    if hasattr(options, 'nologfile') and options.nologfile:
        config['Logging']['logfile'] = ''
    if hasattr(options, 'loglevel') and options.loglevel is not None and options.loglevel != '':
        config['Logging']['level'] = options.loglevel
    if hasattr(options, 'slickurl') and options.slickurl is not None and options.slickurl != '':
        config['Slick']['url'] = options.slickurl
    if hasattr(options, 'logfile') and options.logfile is not None and options.logfile != '':
        config['Logging']['logfile'] = options.logfile
    initialize_logging(config)
    logger = logging.getLogger("narc.main.setup")
    logger.info("Narc is initializing.")
    logger.debug("Configuring a slick connection at url '{}'.", config['Slick']['url'])
    slick = SlickConnection(config['Slick']['url'])
    validate_slick_connection(slick)
    amqp_config = slick.systemconfigurations(AMQPSystemConfiguration).findOne()
    if amqp_config is None:
        raise Exception("No AMQP Connection Information was found")
    assert(isinstance(amqp_config, AMQPSystemConfiguration))
    if not 'AMQP' in config:
        config.add_section("AMQP")
    if not 'hostname' in config['AMQP']:
        config['AMQP']['hostname'] = amqp_config.hostname
    if not 'port' in config['AMQP']:
        config['AMQP']['port'] = str(amqp_config.port)
    if not 'username' in config['AMQP']:
        config['AMQP']['username'] = amqp_config.username
    if not 'password' in config['AMQP']:
        config['AMQP']['password'] = amqp_config.password
    if not 'exchange' in config['AMQP']:
        config['AMQP']['exchange'] = amqp_config.exchangeName
    if not 'virtual host' in config['AMQP']:
        config['AMQP']['virtual host'] = amqp_config.virtualHost

    amqpcon = amqp.AMQPConnection(config)

    return (config, slick, amqpcon)

class MainVars:
    restart = False
    keep_going = True

# these are global variables that are used inside main
def main(args=sys.argv[1:]):
    # parse command line
    parser = argparse.ArgumentParser(description="Narc is a utility that is used to respond to slick events.")
    parser.add_argument('-c', '--config', action='store', default='/etc/narc.conf', dest='configpath', metavar='CONFIGPATH', help="specify the config file narc uses, default=/etc/narc.conf")
    parser.add_argument('-s', '--stdout', action='store_true', default=False, dest='stdout', help="send logs to stdout")
    parser.add_argument('--loglevel', action='store', dest='loglevel', help="Change the default log level from INFO to another level (like DEBUG, WARNING, ERROR, or CRITICAL)")
    parser.add_argument('--slick', action='store', dest='slickurl', metavar='SLICKBASEURL', help='Use the specified url for connecting to slick')
    parser.add_argument('--logfile', action='store', dest='logfile', metavar='LOGFILE', help="Change where the logs go to for this run")
    options = parser.parse_args(args)

    while MainVars.restart or MainVars.keep_going:
        MainVars.restart = False
        MainVars.keep_going = True
        try:
            (configuration, slick, amqpcon) = setup(options)
        except:
            print("ERROR Initializing narc:")
            traceback.print_exc()
            sys.exit(1)

        logger = logging.getLogger('narc.main.main')
        plugins = []

        for entrypoint in pkg_resources.iter_entry_points(group='narc.response'):
            plugin = entrypoint.load()
            plugins.append(plugin(configuration, amqpcon, slick))

        with amqpcon.connection, nested(*amqpcon.channels), nested(*amqpcon.consumers):
            while MainVars.keep_going:
                try:
                    amqpcon.connection.drain_events(timeout=1)
                except socket.timeout:
                    pass

        logger.info("Done with main method, restart={}", MainVars.restart)
        MainVars.keep_going = False

    # sub main:
    #   load configuration
    #   configure logging
    #   initialize connection
    #   load plugins
    #   while not stop:
    #     connection.drain_events(timeout)

def ctlmain(args=sys.argv[1:]):
    parser = argparse.ArgumentParser(description="narcctl is used to control and configure narc.")
    parser.add_argument('-c', '--config', action='store', default='/etc/narc.conf', dest='configpath', metavar='CONFIGPATH', help="specify the config file narc uses, default=/etc/narc.conf")
    parser.add_argument('-l', '--logfile', action='store_false', default=True, dest='nologfile', help="send logs to the narc log file")
    parser.add_argument('--loglevel', action='store', default='INFO', dest='loglevel', help="Change the default log level from INFO to another level (like DEBUG, WARNING, ERROR, or CRITICAL)")
    parser.add_argument('-q', '--quiet', action='store_false', default=True, dest='stdout', help="don't log to stdout")
    parser.add_argument('--slick', action='store', dest='slickurl', metavar='SLICKBASEURL', help='Use the specified url for connecting to slick')
    parser.add_argument('--shutdown', action='store_true', dest='shutdown', default=False, help="Send a shutdown signal to narc.")
    parser.add_argument('--restart', action='store_true', dest='restart', default=False, help="Send a restart signal to narc.")
    options = parser.parse_args(args)
    (configuration, slick, amqpcon) = setup(options)
    if options.shutdown:
        producer = Producer(amqpcon.default_channel, amqpcon.exchange)
        producer.publish("shutdown", "narc.shutdown")
    elif options.restart:
        producer = Producer(amqpcon.default_channel, amqpcon.exchange)
        producer.publish("restart", "narc.shutdown")
