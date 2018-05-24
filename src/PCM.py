# pylint: disable=bad-whitespace,bad-continuation,line-too-long,multiple-statements,trailing-whitespace,trailing-newlines
"""PCM"""

import sys

try:
    from time            import sleep, time
    # ~ from random          import randint # test purpose
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
        self.status = {}
        self.cfgname = cfgname
        signal(SIGHUP, self.handle_sighup)
        self.logger = Logger.Logger()
        self.logger.level = 0
        self.logger.log_time = True
        self.logger.setLogfile('&2')
        self.Configure()
        self.cmdline = Cmdline.Cmdline(args)
        self.enginePIDfile = self.configuration['engine_pid_file']
        self.watcherPIDfile = self.configuration['watcher_pid_file']
        self.engineStatusFile = self.configuration['engine_status_file']
        self.watcherStatusFile = self.configuration['watcher_status_file']
        self.status['engineStartTime'] = None
        self.status['engineUptime'] = 0
        self.setInitialFiles()

    def setInitialFiles(self):
        
        if not isdir(self.configuration['host_dir']): mkdir(self.configuration['host_dir'])
        if not isfile(self.configuration['host_dir']+'/localhost.in'):
            with open(self.configuration['host_dir']+'/localhost.in', 'w') as f:
                f.write("IP_ADDRESS = '127.0.0.1'\n")

    def startEngine(self):
        
        if self.engineStatus(): return False
        with open(self.enginePIDfile,'w') as f: f.write(str(getpid()))
        self.engine = Engine.Engine(self.configuration, self.logger)
        self.engine.run()

    def stopEngine(self):
        try:
            with open(self.enginePIDfile,'r') as f: pid = int(f.readline())
            kill(pid,SIGTERM)
            unlink(self.enginePIDfile)
            unlink(self.engineStatusFile)
            self.logger.log('PCM Engine PID='+str(pid)+' is stopped.')
            print('PCM Engine  stopped.', file=sys.stderr)
        except (AttributeError, ProcessLookupError, FileNotFoundError): #TODO: Handle each exception individually
            print('PCM Engine not running.', file=sys.stderr)

    def engineStatus(self):
        try:
            with open(self.enginePIDfile,'r') as f: pid = int(f.readline())
            with open(self.engineStatusFile,'rb') as f: self.status = loads(f.read())   
            print('PCM Engine is running. PID={} Uptime={}'.format(str(pid),str(self.status['uptime'])), file=sys.stderr)
            return True
        except (AttributeError,OSError) as err:
            try:
                if err.errno == errno.EPERM:
                    print('PCM Engine is running but access is denied. PID='+str(pid), file=sys.stderr)
                    return False
                else: print(str(err), file=sys.stderr)
                return False
            except NameError as ne:
                print('PCM Engine not running.', file=sys.stderr)
                return False

        except EOFError:
            
            print('PCM Engine is running. PID={}'.format(str(pid)), file=sys.stderr)

    def startWatcher(self):
        
        if self.watcherStatus(): return False
        with open(self.watcherPIDfile,'w') as f: f.write(str(getpid()))
        self.watcher = Watcher.Watcher(self.configuration, self.logger)
        self.watcher.run()

    def stopWatcher(self):
        try:
            with open(self.watcherPIDfile,'r') as f: pid = int(f.readline())
            kill(pid,SIGTERM)
            unlink(self.watcherPIDfile)
            unlink(self.watcherStatusFile)
            self.logger.log('PCM Watcher PID='+str(pid)+' is stopped.')
            print('PCM Watcher stopped.', file=sys.stderr)
        except (AttributeError, FileNotFoundError, ProcessLookupError): #TODO: Handle each exception individually
            print('PCM Watcher not running.', file=sys.stderr)

    def watcherStatus(self):
        try:
            with open(self.watcherPIDfile,'r') as f: pid = int(f.readline())
            with open(self.configuration['watcher_status_file'],'rb') as f: self.status = loads(f.read())
            print('PCM Watcher is running. PID={} Uptime={}'.format(str(pid), str(self.status['uptime'])), file=sys.stderr)
            # ~ print(self.status, file=sys.stderr)
            return True
        except (AttributeError,OSError) as err:
            try:
                if err.errno == errno.EPERM:
                    print('PCM Watcher is running but access is denied. PID='+str(pid), file=sys.stderr)
                    return False
                else: print(str(err), file=sys.stderr)
                return False
            except NameError as ne:
                print('PCM Watcher not running.', file=sys.stderr)
                return False

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

    
