# pylint: disable=bad-whitespace,bad-continuation,line-too-long,multiple-statements,trailing-whitespace,trailing-newlines
"""PCM"""

import sys

try:
    from time            import sleep, time
    # ~ from random          import randint # test purpose
    from multiprocessing import Process, Queue
    from signal          import signal, SIGTERM, SIGHUP
    from re              import split as resplit 
    from os              import _exit, getpid, kill, unlink
    import Logger, Cmdline, Server, Watcher

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
        
        self.Configure(self.cfgfile)

    def __init__(self, cfgname = default_cfgname, args = sys.argv):

        self.configuration = {}
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

    def startEngine(self):
        
        with open(self.enginePIDfile,'w') as f: f.write(str(getpid()))
        while True:
            print('hey!')
            sleep(5)

    def stopEngine(self):
        try:
            with open(self.enginePIDfile,'r') as f: pid = int(f.readline())
            kill(pid,SIGTERM)
            unlink(self.enginePIDfile)
            self.logger.log('PCM Engine PID='+str(pid)+' is stopped.')
            print('PCM Engine is stopped.', file=sys.stderr)
        except AttributeError as err: print(str(err))

    def engineStatus(self):
        try:
            with open(self.enginePIDfile,'r') as f: pid = int(f.readline())
            print('PCM Engine is running. PID={}'.format(str(pid)), file=sys.stderr)
            return True
        except (AttributeError,OSError) as err:
            try:
                if err.errno == errno.EPERM:
                    print('PCM Engine is running but access is denied. PID='+str(pid), file=sys.stderr)
                    return False
                else: print(str(err), file=sys.stderr)
                return False
            except NameError as ne:
                print('No PID file found for PCM Engine. '+str(err), file=sys.stderr)
                return False

    def startWatcher(self):
        
        with open(self.watcherPIDfile,'w') as f: f.write(str(getpid()))
        self.watcher = Watcher.Watcher()
        self.watcher.run()

    def stopWatcher(self):
        try:
            with open(self.watcherPIDfile,'r') as f: pid = int(f.readline())
            kill(pid,SIGTERM)
            unlink(self.watcherPIDfile)
            self.logger.log('PCM Watcher PID='+str(pid)+' is stopped.')
            print('PCM Watcher is stopped.', file=sys.stderr)
        except AttributeError as err: print(str(err))

    def watcherStatus(self):
        try:
            with open(self.watcherPIDfile,'r') as f: pid = int(f.readline())
            print('PCM Watcher is running. PID={}'.format(str(pid)), file=sys.stderr)
            return True
        except (AttributeError,OSError) as err:
            try:
                if err.errno == errno.EPERM:
                    print('PCM Watcher is running but access is denied. PID='+str(pid), file=sys.stderr)
                    return False
                else: print(str(err), file=sys.stderr)
                return False
            except NameError as ne:
                print('No PID file found for PCM Watcher. '+str(err), file=sys.stderr)
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

