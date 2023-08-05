import StringIO
from subprocess import PIPE, Popen
import to_sentry.transmitter
import gflags
FLAGS = gflags.FLAGS

gflags.DEFINE_string('message', None, 'A description of what broke')
gflags.DEFINE_string('channel', 'cron', 'Channel name from the config file')


def main(argv, stdin):

    try:
        argv = FLAGS(argv)[1:]
    except gflags.FlagsError, e:
      print '%s\\nUsage: %s ARGS\\n%s' % (e, sys.argv[0], FLAGS)
      return 1
    if not FLAGS.message:
        to_sentry.transmitter.send_old(list(argv), stdin, extra={'deprecation warning': 
                                                                 'to_sentry warning: to_sentry <channel> <message> is deprecated.'})
    elif argv:
        p = Popen(argv, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()
        returncode = p.returncode
        to_sentry.transmitter.send(FLAGS.channel, FLAGS.message, stdout, stderr, extra={'returncode': str(p.returncode)})
    else:
        to_sentry.transmitter.send(FLAGS.channel, FLAGS.message, stdin)

