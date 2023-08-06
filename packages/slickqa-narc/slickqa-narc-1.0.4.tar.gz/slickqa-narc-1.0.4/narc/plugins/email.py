"""
The email responder plugin.  This plugin sends emails whenever a testrun is created / finished.
"""
__author__ = 'jcorbett'

import configparser
import logging
import json
from io import BytesIO
import time

from ..amqp import AMQPConnection

from slickqa import SlickConnection, EmailSystemConfiguration, Testrun, EmailSubscription, Result, ResultStatus, StoredFile
from slickqa import micromodels
from kombu import Consumer, Queue
from kombu.transport.base import Message
from jinja2 import Template
import cairosvg.surface

import pygal
from pygal.style import DefaultStyle, Style

# smtp imports
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
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
            <h1 style="color: #fff; background-image: -webkit-linear-gradient(#A6000D, #650207); background-image: -moz-linear-gradient(#A6000D, #650207); background-image: -ms-linear-gradient(#A6000D, #650207); border-radius: .2in .2in .2in .2in; margin: .3in; padding: .1in .2in .1in .2in;"><a href="{{url(testrun)}}" style="text-decoration: none; color: white">{{subject}}</a></h1>
        </div>
        <table style="margin-left: .5in; color: #d3d2d2; border-spacing: 0">
            <tr style="color: #d3d2d2">
                <td rowspan="{{len(testrun.summary.statusListOrdered) + 1}}"><img src="cid:{{image_file_name}}" alt="chart" /></td>
            {% for status in testrun.summary.statusListOrdered %}
                <td style="padding-top: 0; padding-bottom: .1in; vertical-align: text-top"><a href="{{url(testrun, status)}}" style="text-decoration: none"><span style="color: {{colors[status]}}; font-size: 2.5em">{{status}}</span></a></td>
                <td style="padding-top: 0; padding-bottom: .1in; padding-left: .3in; vertical-align: text-top"><span style="font-size: 2.5em">{{getattr(testrun.summary.resultsByStatus, status)}}</span></td>
            </tr>
            <tr style="color: #d3d2d2">
            {% endfor %}
                <td style="border-top: 1px solid white; border-collapse:collapse; vertical-align: text-top; padding-top: .1in;"><span style="font-size: 2.5em">Total tests</span></td>
                <td style="border-top: 1px solid white; border-collapse:collapse; vertical-align: text-top; padding-top: .1in; padding-left: .3in;"><span style="font-size: 2.5em">{{testrun.summary.total}}</span></td>
            </tr>
        </table>
        {% if len(failed_results) > 0 %}
        <hr />
        <h1>Failed Results</h1>
        {% for result in failed_results %}
            <div style="margin-left: .2in"><a href="{{url(result)}}" style="text-decoration: none; color: {{colors['FAIL']}}; font-size: 2em">{{result.testcase.name}}</a></div>
            <pre style="margin-left: .5in">{{result.reason}}</pre>
            <div style="margin-left: .5in; margin-bottom: .1in">Files:
            {% for storedfile in result.files %}
                <a href="{{url(storedfile)}}">{{storedfile.filename}}</a>
            {% endfor %}
            </div>
        {% endfor %}
        {% endif %}
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
            to = self.get_addresses_for(update.after)
            if len(to) > 0:
                self.logger.info("Testrun with id {} and name {} just finished, generating email to subscribers: {}", update.after.id, update.after.name, ', '.join(to))
            else:
                self.logger.info("Testrun with id {} and name {} just finished, but no emails are subscribed.", update.after.id, update.after.name)
                return
            (subject_template, email_template) = self.get_templates_for(update.after)
            image_file_name = "chart-{}.png".format(str(int(time.time())))
            email_template = Template(email_template)
            subject = subject_template.format(testrun=update.after)

            #TODO: fix after creating results query
            failed_results = self.slick.results.find(testrunid=update.after.id, status=ResultStatus.FAIL)
            text = email_template.render(testrun=update.after, subject=subject, colors=EmailResponder.colors, image_file_name=image_file_name, url=self.url, failed_results=failed_results, getattr=getattr, len=len)
            image = self.generate_chart_for(update.after)
            self.mail(to, subject, text, image, image_file_name)

    def generate_chart_for(self, testrun):
        assert(isinstance(testrun, Testrun))
        colors = []
        for status in testrun.summary.statusListOrdered:
            colors.append(EmailResponder.colors[status])
        mystyle = Style(background='transparent',
                        plot_background='transparent',
                        colors=colors,
                        foreground='#d2d3d3',
                        foreground_light='#eee',
                        foreground_dark='#555')
        config = pygal.Config()
        config.show_legend = False
        pie_chart = pygal.Pie(config, width=400, height=300, style=mystyle)
        for status in testrun.summary.statusListOrdered:
            pie_chart.add(status, getattr(testrun.summary.resultsByStatus, status))
        fakefile_svg = BytesIO()
        fakefile_svg.write(pie_chart.render())
        fakefile_svg.seek(0)

        # this is what render_to_png does, but this way we don't have to write to a file
        return cairosvg.surface.PNGSurface.convert(file_obj=fakefile_svg)


    def mail(self, to, subject, text, image, image_file_name):
        # build a list from 'to'
        msg = MIMEMultipart()
        msg['From'] = self.email_settings.sender
        msg['To'] = ', '.join(to)
        msg['Subject'] = subject
        msg.attach(MIMEText(text, 'html'))

        img = MIMEImage(image)
        img.add_header('Content-ID', '<' + image_file_name + '>')
        msg.attach(img)

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

    def url(self, param, status=None):
        """Return a url based on the parameter passed in."""
        base_url = self.slick.baseUrl[0:-4]
        if isinstance(param, Testrun):
            if status is None:
                return "{}/#/reports/testrunsummary/{}".format(base_url, param.id)
            else:
                return "{}/#/reports/testrundetail/{}?only={}".format(base_url, param.id, status)
        elif isinstance(param, Result):
            return "{}/#/reports/result/{}".format(base_url, param.id)
        elif isinstance(param, StoredFile):
            return "{}/api/files/{}/content/{}".format(base_url, param.id, param.filename)


    def get_templates_for(self, testrun):
        assert(isinstance(testrun, Testrun))
        return (EmailResponder.default_subject_template, EmailResponder.default_email_template)

    def get_addresses_for(self, testrun):
        assert(isinstance(testrun, Testrun))
        email_addresses = self.slick.systemconfigurations(EmailSubscription).find()
        addresses = []
        for email_address in email_addresses:
            if email_address.enabled:
                for subscription in email_address.subscriptions:
                    if subscription.subscriptionType == 'Global':
                        addresses.append(email_address.name)
                    elif subscription.subscriptionType == 'Project' and testrun.project is not None and subscription.subscriptionValue == testrun.project.id:
                        addresses.append(email_address.name)
                    elif subscription.subscriptionType == 'Testplan' and testrun.testplan is not None and subscription.subscriptionValue == testrun.testplan.id:
                        addresses.append(email_address.name)
                    elif subscription.subscriptionType == 'Release' and testrun.release is not None and subscription.subscriptionValue == testrun.release.releaseId:
                        addresses.append(email_address.name)
                    elif subscription.subscriptionType == 'Configuration' and testrun.config is not None and subscription.subscriptionValue == testrun.config.configId:
                        addresses.append(email_address.name)
        return addresses





