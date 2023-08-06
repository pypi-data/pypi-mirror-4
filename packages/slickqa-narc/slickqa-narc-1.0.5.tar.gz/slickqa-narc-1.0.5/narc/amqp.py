"""
This module contains the class we use to connect to AMQP Server.
"""
__author__ = 'jcorbett'

import logging
from kombu import Connection, Consumer, Exchange

class AMQPConnectionError(BaseException):
    pass

class AMQPConnection(object):
    """
    A class representing a connection to an amqp broker.
    """

    def __init__(self, configuration):
        self.logger = logging.getLogger('narc.amqp.AMQPConnection')
        self.url = str.format("amqp://{hostname}:{port}", **dict(configuration['AMQP'].items()))
        if 'virtual host' in configuration['AMQP'] and configuration['AMQP']['virtual host'] != '':
            self.url = str.format("{}/{}", self.url, configuration['AMQP']['virtual host'])
        self.logger.debug("AMQPConnection configured with url {}", self.url)
        self.exchange = Exchange(configuration['AMQP'].get('exchange', "amqp.topic"), type='topic')
        self.logger.debug("AMQPConnection is using exchange {}", self.exchange)
        if 'username' in configuration['AMQP'] and 'password' in configuration['AMQP']:
            username = configuration['AMQP']['username']
            password = configuration['AMQP']['password']
            self.logger.debug("Using username {} and password {} to connect to AMQP Broker", username, password)
            self.connection = Connection(self.url, userid=username, password=password)
        else:
            self.connection = Connection(self.url)

        self.channels = []
        self.consumers = []
        self.default_channel = self.connection.default_channel

    def add_channel(self):
        self.logger.debug("Adding channel number {} to the list of channels", len(self.channels) + 1)
        self.channels.append(self.connection.channel())
        return self.channels[-1]

    def add_consumer(self, consumer):
        assert(isinstance(consumer, Consumer))
        self.logger.debug("Adding consumer number {} to the list of consumers", len(self.consumers) + 1)
        self.consumers.append(consumer)


