# pylint: disable=bad-whitespace,bad-continuation,line-too-long,multiple-statements,trailing-whitespace,trailing-newlines
"""PCM"""

import sys

try:
    from time            import sleep, time
    from multiprocessing import Process, Queue
    from signal          import signal, SIGTERM, SIGHUP
    from re              import split as resplit 
    from os              import _exit, getpid, kill, unlink, mkdir
    from os.path         import isfile, isdir
    from pickle          import dumps, loads
    import Logger, Cmdline, Server, Watcher, Engine

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

class PCM:
    """PCM"""
    default_cfgname = './pcm.cfg'

    def handle_sighup(self, signum, frame):
        
        self.Configure()

    def __init__(self, cfgname = default_cfgname, args = sys.argv):

        self.configuration = {}
        self.state = {}
        self.cfgname = cfgname
        signal(SIGHUP, self.handle_sighup)
        self.logger = Logger.Logger()
        self.logger.level = 0
        self.logger.log_time = True
        self.logger.setLogfile('&2')
        self.cmdline = Cmdline.Cmdline(args)
        self.Configure()
        self.logger.setLogLevel(int(self.configuration['log_level']))
        self.setInitialFiles()

    def setInitialFiles(self):
        
        if not isdir(self.configuration['host_dir']): mkdir(self.configuration['host_dir'])
        if not isfile(self.configuration['host_dir']+'/localhost.in'):
            with open(self.configuration['host_dir']+'/localhost.in', 'w') as f:
                f.write("IP_ADDRESS = '127.0.0.1'\n")

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
            return True
        except Exception as e:
            self.logger.log(' *** Configuration error! − '+str(e)+' ***', 4)
            return False

    
