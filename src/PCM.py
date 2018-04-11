# pylint: disable=bad-whitespace,bad-continuation,line-too-long,multiple-statements,trailing-whitespace,trailing-newlines
"""PCM"""

import sys

try:
    from time            import sleep # test purpose only!
    from random          import randint # test purpose
    from multiprocessing import Process, Queue
    from signal          import signal, SIGTERM, SIGHUP
    from re              import split as resplit 
    from os              import _exit
    import Logger, Cmdline, Server

except ImportError as e:

    print(str(e), file=sys.stderr)
    print('Cannot find the module(s) listed above. Exiting.', file=sys.stderr)
    sys.exit(1)

def listprint(l):
    """Return a list applying the str function on every elements. If the argument is a scalar then just return str(element)."""
    try: return '\n'.join(map(str, l))
    except TypeError: return str(l)

def listuniq(l):
    """Return a list of unique elements of a list, conserving the initial order."""
    oset = OrderedSet()
    for elem in l: oset.add(elem)
    return list(oset)

def str2bool(v, true=("yes", "true", "1")):
    """Convert "true" string to a boolean."""
    return v.lower() in true

def process_request(request):
    
    return request

class PCM:
    """PCM"""
    default_cfgname = './pcm.cfg'

    def handle_sighup(self, signum, frame):
        
        self.Configure(self.cfgfile)

    def __init__(self, cfgname = default_cfgname, args = sys.argv):

        self.configuration = {}
        self.cfgname = cfgname
        signal(SIGHUP, self.handle_sighup)
        self.logger = Logger.Logger()
        self.logger.level = 0
        self.logger.setLogfile('&2')
        self.Configure()
        self.cmdline = Cmdline.Cmdline(args)
        self.server = Server.Server(self.configuration, self.logger)

    def Configure(self):
        
        try:
            with open(self.cfgname) as f:
                for l in f:
                    line = l.strip()
                    try:
                        if line[0] == '#': continue
                        k,v = resplit(' |\t',line,1)
                        self.configuration[k] = v.strip()
                    except IndexError: continue # empty line
            try: self.logger.setLogfile(self.configuration['log_filename'])
            except KeyError: self.logger.setLogfile('./pcm.log')
            self.logger.log('Configuration OK')
            return True
        except Exception as e:
            self.logger.log(' *** Configuration error! − '+str(e)+' ***')
            return False


