from ConfigParser import ConfigParser, Error


import gflags 
FLAGS = gflags.FLAGS 

gflags.DEFINE_string('config', '/etc/to_sentry.conf', 
                     'Location of the sentry configuration file.')

class ToSentryConfigParser(ConfigParser):


    def __init__(self, *args, **kwargs):
        ConfigParser.__init__(self, *args, **kwargs)
        if not self.read(FLAGS.config):
            raise IOError('%r not readable.' % (FLAGS.config,))
        
    def __getitem__(self, key):
        try:
            return self.get(key, 'url')
        except Error:
            if key.startswith('http://') or key.startswith('https://'):
                return key
            else:
                raise Error(key)
    
