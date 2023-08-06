"""
Logging related functions and classes.
"""
__author__ = 'jcorbett'

import logging
import logging.handlers
import configparser
import sys

class StrFormatLogRecord(logging.LogRecord):
    """
    Even though you can select '{' as the style for the formatter class, you still can't use
    {} formatting for your message.  This is stupid, so this class will fix it.
    """

    def getMessage(self):
        msg = str(self.msg)
        if self.args:
            # potential bug here, if they provide a 0th argument, but don't use it in the message.
            # the old formatting would have thrown an exception in that case, and it still will.
            if '{}' in msg or '{0}' in msg:
                msg = msg.format(*self.args)
            else:
                msg = msg % self.args
        return msg

# Allow {} style formatting of log messages, which is far superior!
logging.setLogRecordFactory(StrFormatLogRecord)

def initialize_logging(configuration):
    assert(isinstance(configuration, configparser.ConfigParser))
    logfile = configuration['Logging'].get('logfile')
    level = configuration['Logging'].get('level', 'DEBUG')
    stdout = configuration['Logging'].getboolean('stdout', False)
    format = configuration['Logging'].get('format', '[{process:<6}|{asctime}|{levelname:<8}|{name}]: {message}')
    dateformat = configuration['Logging'].get('dateformat', '%x %I:%M:%S %p')
    handlers = []
    formatter = logging.Formatter(fmt=format, datefmt=dateformat, style='{')
    root_logger = logging.getLogger()
    exc_info = None
    try:
        if logfile is not None and logfile != '':
            handlers.append(logging.handlers.WatchedFileHandler(logfile))
            if stdout:
                handlers.append(logging.StreamHandler())
        else:
            # if there is no logfile, you have to have stdout logging
            handlers.append(logging.StreamHandler())
    except PermissionError:
        handlers = [logging.StreamHandler(),]
        exc_info = sys.exc_info()
    root_logger.setLevel(level)
    if root_logger.hasHandlers():
        for handler in root_logger.handlers:
            root_logger.removeHandler(handler)
    for handler in handlers:
        handler.setFormatter(formatter)
        root_logger.addHandler(handler)
    if exc_info is not None:
        logger = logging.getLogger("narc.main.initialize_logging")
        logger.warning("Unable to write to log file {}: ", logfile, exc_info=exc_info)

