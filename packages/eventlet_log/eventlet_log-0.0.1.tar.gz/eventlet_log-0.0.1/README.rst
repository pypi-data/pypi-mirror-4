Eventlet_log -- Damn simple logger
==================================

About
-----

Simple wrapper around logging module compatible with eventlet.

API
---

``create_logger`` function takes logger name and optional format and level arguments and return (log, log_exc, logger) tuple.

``log`` is just logger.info -- prints given message with INFO level.

``log_exc`` calls logger.exception and prints given message along with stacktrace.

``logger`` is instance of logging.Logger class.

Usage
-----

::

    from eventlet_log import create_logger
    (log, log_exc, _) = create_logger('younameit')

    log('Hello world')

    try:
        1/0
    except ZeroDivisionError:
        log_exc('Smth happens')


Install
-------

~/yourvirtualenv/python setup.py install

pip install eventlet_log

License
-------

The MIT License, in LICENSE file.
