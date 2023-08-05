from to_sentry.config_parser import ToSentryConfigParser

import logging
import os
import raven
import raven.events
import urllib2
import warnings

import gflags 
FLAGS = gflags.FLAGS 

gflags.DEFINE_integer('digits', 8, 'Length of stderr and stdout line numbers.', lower_bound=1)
gflags.DEFINE_boolean('ignore-stderr', False, 'When running in "exec mode" ignore stderr')
gflags.DEFINE_boolean('ignore-stdout', False, 'When running in "exec mode" ignore stdout')
gflags.DEFINE_boolean('ignore-exitcode', False, 'When running in "exec mode" ignore exit code')

def usage():
    print "Usage: to_sentry <sentry feed> Subject line ... "


def format_text(handle, text):
    if not text:
        raise StopIteration()
    formatter = handle + ".%%0%dd" % (FLAGS.digits,)
    for x, line in enumerate(text.split('\n')):
        line = line.rstrip()
        key = formatter % (x,)
        if line:
            yield key, line


def send(channel, message, stdout, stderr=None, client_factory=raven.Client, extra=None):
    if not extra:
        extra = {}
    if hasattr(stdout, 'read'):
        stdout = stdout.read()
    if stderr and hasattr(stderr, 'read'):
        stderr = stderr.read()
    if getattr(FLAGS, 'ignore-stdout'):
        stdout = ''
    if getattr(FLAGS, 'ignore-stderr'):
        stderr = ''
    if getattr(FLAGS, 'ignore-exitcode'):
        if 'exit code' in extra:
            del(extra['exit code'])
    
    logger = logging.getLogger("sentry.errors")
    handler = logging.StreamHandler()
    formatter = logging.Formatter(("[%(levelname)s] "
                                   "%(name)s: "
                                   "%(message)s\n\nOriginal "
                                   "application "
                                   "error "
                                   "follows:\n") + stdout)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        client = client_factory(dsn=ToSentryConfigParser()[channel])
        if stdout or stderr or ('exit code' in extra and int(extra['exit code']) != 0):
            for key, value in format_text('stdout', stdout):
                extra[key] = value
            for key, value in format_text('stderr', stderr):
                extra[key] = value 
            for key, value in os.environ.items():
                extra["env." + key] = value
            client.capture('Message',
                           message=message,
                           data = None,
                           extra = extra)


def send_old(argv, stdin, client_factory=raven.Client, extra=None):
    return send(argv[0], ' '.join(argv[1:]), stdin, extra=extra)
