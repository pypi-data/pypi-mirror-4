from to_sentry.config_parser import ToSentryConfigParser

import logging
import os
import raven
import raven.events
import urllib2
import warnings


def usage():
    print "Usage: to_sentry <sentry feed> Subject line ... "


def format_text(handle, text):
    formatter = handle + ".%08d"
    for x, line in enumerate(text.split('\n')):
        line = line.rstrip()
        key = formatter % (x,)
        if line:
            yield key, line


def send(argv, stdin, client_factory=raven.Client):
    if len(argv) < 2:
        usage()
        return 1

    data = stdin.read()
    logger = logging.getLogger("sentry.errors")
    handler = logging.StreamHandler()
    formatter = logging.Formatter(("[%(levelname)s] "
                                   "%(name)s: "
                                   "%(message)s\n\nOriginal "
                                   "application "
                                   "error "
                                   "follows:\n") + data)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        client = client_factory(dsn=ToSentryConfigParser()[argv[1]])
        if data:
            extra = {}
            for key, value in format_text('stdout', data):
                extra[key] = value
            for key, value in os.environ.items():
                extra["env." + key] = value
            client.capture('Message',
                           message=' '.join(argv[2:]),
                           data = None,
                           extra = extra)
