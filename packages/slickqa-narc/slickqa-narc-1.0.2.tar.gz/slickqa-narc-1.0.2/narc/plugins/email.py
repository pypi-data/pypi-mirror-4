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
from jinja2 import Template
import pygal

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

    default_subject_template = "Results of {testrun.name} on {testrun.project.name} for Release {testrun.release.name} build {testrun.build.name}"

    default_email_template = """
    <div style="background: #000; color: #d3d2d2; padding: 0 0 .5in 0;">
        <div style="display: inline-block">
            <h1 style="color: #fff; background-image: -webkit-linear-gradient(#A6000D, #650207); background-image: -moz-linear-gradient(#A6000D, #650207); background-image: -ms-linear-gradient(#A6000D, #650207); border-radius: .2in .2in .2in .2in; margin: .3in; padding: .1in .2in .1in .2in;"><a href="{{testrun_link}}" style="text-decoration: none; color: white">{{subject}}</a></h1>
        </div>
        <table style="border: 1px solid white; padding: .1in; border-collapse:collapse; margin-left: .5in; color: #d3d2d2">
            <tr style="border: 1px solid white; padding: .1in; border-collapse:collapse; color: #d3d2d2">
                <td style="border: 1px solid white; padding: .1in; border-collapse:collapse;" rowspan="{{len(testrun.summary.statusListOrdered)}}">Image goes here</td>
            {% for status in testrun.summary.statusListOrdered %}
                <td style="border: 1px solid white; padding: .1in; border-collapse:collapse;"><span style="color: {{colors[status]}}; font-size: 1.5em">{{status}}</span></td>
                <td style="border: 1px solid white; padding: .1in; border-collapse:collapse;"><span style="font-size: 1.5em">{{getattr(testrun.summary.resultsByStatus, status)}}</span></td>
            </tr>
            <tr style="border: 1px solid white; padding: .1in; border-collapse:collapse; color: #d3d2d2">
            {% endfor %}
                <td style="border: 1px solid white; padding: .1in; border-collapse:collapse;" colspan="3"><span style="font-size: 1.5em">Total tests: {{testrun.summary.total}}</span></td>
            </tr>
        </table>
    </div>
    """

    colors = {
        "PASS": "#008000",
        "FAIL": "#ff0000",
        "BROKEN_TEST": "#ffac00",
        "SKIPPED": "#bdb76b",
        "NOT_TESTED": "#1e90ff",
        "NO_RESULT": "#c0c0c0",
        "CANCELLED": "#a0522d"
    }

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
            (subject_template, email_template) = self.get_templates_for(update.after)
            # take off the api portion of the url
            testrunlink = self.slick.baseUrl[0:-3]
            testrunlink = testrunlink + "#/reports/testrunsummary/" + update.after.id
            email_template = Template(email_template)
            subject = subject_template.format(testrun=update.after)
            text = email_template.render(testrun=update.after, subject=subject, colors=EmailResponder.colors, testrun_link=testrunlink, getattr=getattr, len=len)
            to = self.get_addresses_for(update.after)
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

    def get_templates_for(self, testrun):
        assert(isinstance(testrun, Testrun))
        return (EmailResponder.default_subject_template, EmailResponder.default_email_template)

    def get_addresses_for(self, testrun):
        assert(isinstance(testrun, Testrun))
        return "jasoncorbett@gmail.com"




