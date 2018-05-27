# pylint: disable=bad-whitespace,bad-continuation,line-too-long,multiple-statements,trailing-whitespace,trailing-newlines,invalid-name,trailing-whitespace
# -*- coding: UTF-8 -*-
"""PCM Daemon class."""
import sys
try:
    from random import randint
    from re import split as resplit
    from time import time, sleep
    from pickle import dumps, loads
    from os import getpid, kill, unlink, path
    from signal import SIGTERM, SIGHUP
    from psutil import process_iter, Process
except ImportError as e:
    print(str(e), file=sys.stderr)
    print('Cannot find the module(s) listed above. Exiting.', file=sys.stderr)
    sys.exit(1)

class Daemon:
    def __init__(self, configuration, logger, name):
        self.state = {}
        self.logger = logger
        self.name = name
        self.configuration = configuration
        self.set_initial_state()
  
    def set_initial_state(self):
        self.state['name'] = self.name
        self.configuration['name'] = self.name
        self.state['startTime'] = time()
        self.state['uptime'] = 0
        self.state['startReportTime'] = time()
        self.state['filename'] = self.configuration['pcm_dir']+'/'+self.state['name'].lower()+'.state'

    def process_exists(self):
        """Return True if the process is found in the processes table."""
        cmdline = [path.basename(sys.executable),sys.argv[0],self.state['name'].lower()]
        for p in process_iter():
            if p.cmdline() == cmdline: return p.pid
        return False

    def load_state(self):
        """Load daemon state from state file."""
        try:
            with open(self.state['filename'], 'rb') as f:
                self.state = loads(f.read())
        except FileNotFoundError: self.set_initial_state()
        except (Exception) as e: print(str(e))

    def save_state(self):
        """Write daemon state to state file."""
        try:
            with open(self.state['filename'], 'wb') as f:
                f.write(dumps(self.state))
        except (Exception) as e: print(str(e))

    def start(self):
        print(self.state['name']+' starts. PID={}'.format(str(getpid())), file=sys.stderr)
        self.save_state()
        self.logger.log(self.state['name']+' starts. PID={}'.format(str(getpid())), 1)

    def stop(self):
        """Stop the daemon."""
        pid = self.process_exists()
        if pid:
            kill(pid,SIGTERM)
            try: unlink(self.state['filename'])
            except FileNotFoundError as err: print(str(err), file=sys.stderr)
            print(self.state['name']+' stopped.', file=sys.stderr)
            self.logger.log(self.state['name']+' PID='+str(pid)+' stopped.', 1)
            return True
        print(self.state['name']+' not running.', file=sys.stderr)
        return False

    def status(self):
        """Check if the daemon is running."""
        pid = self.process_exists()
        if pid:
            uptime = time() - Process(pid).create_time()
            print(self.state['name']+' is running. PID={} Uptime={}'.format(str(pid),str(int(uptime))), file=sys.stderr)
            return True
        print(self.state['name']+' not running.', file=sys.stderr)
        return False

    def run(self):
        """Daemon main loop."""
        while True:
            self.load_state()
            self.state['uptime'] = time() - Process(getpid()).create_time()
            self.state['reportTime'] = time() - self.state['startReportTime']
            pp = self.process()
            self.save_state()
            sleep(5)

    def process(self):
        """Daemon main procedure."""
        if self.state['reportTime'] >= int(self.configuration['report_time']):
            self.logger.log(self.state['name']+' OK, uptime is {}.'.format(str(int(self.state['uptime']))))
            self.state['startReportTime'] = time()


