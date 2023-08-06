"""
The email responder plugin.  This plugin sends emails whenever a testrun is created / finished.
"""
__author__ = 'jcorbett'

import configparser
import logging
import json

from ..amqp import AMQPConnection

from slickqa import SlickConnection, EmailSystemConfiguration, Testrun
from slickqa import micromodels
from kombu import Consumer, Queue
from kombu.transport.base import Message

# smtp imports
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders


class TestrunUpdateMessage(micromodels.Model):
    before = micromodels.ModelField(Testrun)
    after = micromodels.ModelField(Testrun)

class EmailResponder(object):
    """The email auto responder plugin"""

    def __init__(self, configuration, amqpcon, slick):
        assert(isinstance(configuration, configparser.ConfigParser))
        assert(isinstance(amqpcon, AMQPConnection))
        assert(isinstance(slick, SlickConnection))
        self.configuration = configuration
        self.amqpcon = amqpcon
        self.logger = logging.getLogger('narc.plugins.email.EmailResponder')
        self.logger.debug("Email Responder is gathering settings from slick.")
        self.slick = slick
        self.email_settings = self.slick.systemconfigurations(EmailSystemConfiguration).findOne()
        self.configured = False
        if self.email_settings is not None:
            assert(isinstance(self.email_settings, EmailSystemConfiguration))
            if self.email_settings.enabled:
                self.configured = True
                self.logger.debug("Recieved email settings: {}", self.email_settings.to_json())
            else:
                self.logger.info("Email responses have been disabled by email system configuration retrieved from slick.")

        if self.configured:
            self.channel = amqpcon.add_channel()
            self.queue = Queue('narc_testrun_email_response', exchange=amqpcon.exchange, routing_key='update.Testrun', durable=True)
            self.consumer = Consumer(self.channel, queues=[self.queue,], callbacks=[self.testrun_updated,])
            amqpcon.add_consumer(self.consumer)

    def testrun_updated(self, body, message):
        assert(isinstance(message, Message))
        if not message.acknowledged:
            message.ack()
        update = TestrunUpdateMessage.from_dict(body)
        if update.before.finished is False and update.after.finished is True:
            self.logger.info("Testrun with id {} and name {} just finished.", update.after.id, update.after.name)
            text = """
            <h1>Testrun {testrun.name} Results</h1>
            Total tests: {testrun.summary.total}
            PASS: {testrun.summary.resultsByStatus.PASS}
            """.format(testrun=update.after)
            subject = "Results for {testrun.name}".format(testrun=update.after)
            to = "jasoncorbett@gmail.com"
            self.mail(to, subject, text)

    def mail(self, to, subject, text):
        # build a list from 'to'
        to = to.strip()
        to = to.split(',')
        msg = MIMEMultipart()
        msg['From'] = self.email_settings.sender
        msg['To'] = ', '.join(to)
        msg['Subject'] = subject
        msg.attach(MIMEText(text, 'html'))

        #if os.path.exists(image):
        #    fp = open(image, 'rb')
        #    img = MIMEImage(fp.read())
        #    fp.close()
        #    img.add_header('Content-ID', '<result.png>')
        #    msg.attach(img)

        mailServer = None
        if self.email_settings.ssl:
            mailServer = smtplib.SMTP_SSL(self.email_settings.smtpHostname, port=self.email_settings.smtpPort)
        else:
            mailServer = smtplib.SMTP(self.email_settings.smtpHostname, port=self.email_settings.smtpPort)
        mailServer.ehlo()
        if self.email_settings.smtpUsername is not None and self.email_settings.smtpUsername != "":
            mailServer.login(self.email_settings.smtpUsername, self.email_settings.smtpPassword)
        mailServer.sendmail(self.email_settings.sender, to, msg.as_string())
        # Should be mailServer.quit(), but that crashes...
        mailServer.close()





