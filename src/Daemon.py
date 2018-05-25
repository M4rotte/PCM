#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import sys

try:
    
    from random import randint
    from time import time, sleep
    from pickle import dumps, loads
    from os import getpid, kill, unlink, _exit, path
    from signal import signal, SIGTERM, SIGHUP
    from psutil import process_iter

except ImportError as e:

    print(str(e), file=sys.stderr)
    print('Cannot find the module(s) listed above. Exiting.', file=sys.stderr)
    sys.exit(1)

class Daemon:

    def __init__(self, configuration, logger, name):
        
        self.state = {}
        self.logger = logger
        self.state['name'] = name
        self.state['startTime'] = None
        self.state['uptime'] = 0
        self.configuration = configuration
        self.state['filename'] = self.configuration[self.state['name'].lower()+'_state_file']

    def lucky(self, possible):
        
        if randint(1, possible) == 1: return True
        else: return False

    def process_exists(self):
                
        cmdline = [path.basename(sys.executable),sys.argv[0],self.state['name'].lower()]
        for p in process_iter():
            if p.cmdline() == cmdline: return p.pid
        return False

    def start(self):

        print(self.state['name']+' starts. PID={}'.format(str(getpid())), file=sys.stderr)

    def stop(self):
        
        pid = self.process_exists()
        if pid:
            kill(pid,SIGTERM)
            unlink(self.state['filename'])
            print(self.state['name']+' stopped.', file=sys.stderr)
            self.logger.log(self.state['name']+' PID='+str(pid)+' stopped.', 1)
            return True
        else:
            print(self.state['name']+' not running.', file=sys.stderr)
            return False

    def status(self):
        
        pid = self.process_exists()
        if pid:
            print(self.state['name']+' is running. PID={}'.format(str(pid)), file=sys.stderr)
            return True
        else:
            print(self.state['name']+' not running.', file=sys.stderr)
            return False


    def run(self):
    
        self.state['startTime'] = int(time())
        print(self.state['name']+' starts. PID={}'.format(str(getpid())), file=sys.stderr)
        self.logger.log(self.state['name']+' starts. PID={}'.format(str(getpid())), 1)
        while True:
            try:
                with open(self.state['filename'], 'rb') as f:
                    self.state = loads(f.read())
                    self.state['uptime'] = int(time()) - self.state['startTime']
            except (FileNotFoundError, EOFError): pass
            with open(self.state['filename'], 'wb') as f:
                f.write(dumps(self.state))
            self.process()
            sleep(1)

    def process(self):
        
        if self.lucky(10): self.logger.log(self.state['name']+' OK, uptime is {}.'.format(self.state['uptime']))

