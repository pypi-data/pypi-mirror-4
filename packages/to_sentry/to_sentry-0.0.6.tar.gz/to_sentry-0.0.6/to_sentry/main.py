import StringIO
from subprocess import PIPE, Popen
import to_sentry
import to_sentry.transmitter
import gflags
import sys
FLAGS = gflags.FLAGS

gflags.DEFINE_string('message', None, 'A description of what broke')
gflags.DEFINE_string('channel', 'cron', 'Channel name from the config file')
gflags.DEFINE_bool('version', False, 'Show the current version number')
gflags.DEFINE_string('version_check', None, 'Test if the version number is at least this large.  If blank, returns version number')


def main(argv, stdin):
    try:
        if len(argv) <= 1:
            print 'Usage: %s ARGS\\n%s' % (sys.argv[0], FLAGS)
            return 1
        argv = FLAGS(argv)[1:]
    except gflags.FlagsError, e:
        print '%s\\nUsage: %s ARGS\\n%s' % (e, sys.argv[0], FLAGS)
        return 1
    if FLAGS.version or FLAGS.version_check:
        if FLAGS.version:
            print "to_sentry:  %d.%d.%d" % to_sentry.VERSION
        if FLAGS.version_check:
            version = tuple(map(int, FLAGS.version_check.split('.')))
            return not(version <= to_sentry.VERSION)
        else:
            return 0
    elif not FLAGS.message:
        to_sentry.transmitter.send_old(list(argv), stdin, extra={'deprecation warning': 
                                                                 'to_sentry warning: to_sentry <channel> <message> is deprecated.'})
    elif argv:
        p = Popen(argv, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()
        returncode = p.returncode
        to_sentry.transmitter.send(FLAGS.channel, FLAGS.message, stdout, stderr, extra={'returncode': str(p.returncode)})
    else:
        to_sentry.transmitter.send(FLAGS.channel, FLAGS.message, stdin)

