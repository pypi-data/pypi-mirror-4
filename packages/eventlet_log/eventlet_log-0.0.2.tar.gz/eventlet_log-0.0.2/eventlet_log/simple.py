# -*- coding: utf-8 -*-

import eventlet
from eventlet.green import thread, threading

import logging
# from OpenStack Swift
logging.thread = eventlet.green.thread
logging.threading = eventlet.green.threading
logging._lock = logging.threading.RLock()


def create_generic_logger(name, handler, format, level):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    handler.setLevel(level)
    formatter = logging.Formatter(format)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    log = logger.info
    log_exc = logger.exception

    return (log, log_exc, logger)


def create_logger(name, format='%(message)s', level=logging.DEBUG):
    '''
    Create eventlet compatible logger with given *name*, *format* and
    *level*.
    If format is not given, logger will print only message.
    Default log level -- DEBUG.
    Returns (log, log_exc, logger), where:
      log is wrapper around *logger.info*
      log_exc is wrapper around *logger.excption*
      logger -- is logger itself
    '''
    return create_generic_logger(name, logging.StreamHandler(),
                                 format, level)

def create_file_logger(name, filename,
                       format='%(message)s', level=logging.DEBUG):
    return create_generic_logger(name, logging.FileHandler(filename),
                                 format, level)
