"""
Internal control of narc.  These plugins will shutdown or restart the program.
"""
__author__ = 'jcorbett'

import logging

from kombu import Consumer, Queue
from kombu.transport.base import Message

from ..amqp import AMQPConnection
from ..main import MainVars

class ShutdownRestartPlugin(object):

    def __init__(self, config, conn, slick):
        assert(isinstance(conn, AMQPConnection))
        self.queue = Queue('narc_internal_shutdown', exchange=conn.exchange, routing_key='narc.shutdown', durable=False, exclusive=True)
        self.consumer = Consumer(conn.default_channel,queues=[self.queue,], callbacks=[self.on_shutdown_message,])
        conn.add_consumer(self.consumer)
        self.logger = logging.getLogger('narc.plugins.internal.ShutdownRestartPlugin')
        self.logger.debug('Plugin initialized.')

    def on_shutdown_message(self, body, message):
        assert(isinstance(message, Message))
        if not message.acknowledged:
            message.ack()
        if body == 'shutdown':
            MainVars.keep_going = False
            self.logger.info("Sending shutdown signal after receiving message.")
        elif body == 'restart':
            MainVars.keep_going = False
            MainVars.restart = True
            self.logger.info("Sending restart signal after receiving message.")

