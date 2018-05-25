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
        self.name = name
        self.configuration = configuration
        self.set_initial_state(name, self.configuration)
    
    def set_initial_state(self, name, configuration):

        self.state['name'] = name
        self.state['startTime'] = int(time())
        self.state['uptime'] = 0
        self.state['filename'] = configuration['pcm_dir']+'/'+self.state['name'].lower()+'.state'

    def lucky(self, chance):
        
        if randint(1, chance) == 1: return True
        else: return False

    def process_exists(self):
                
        cmdline = [path.basename(sys.executable),sys.argv[0],self.state['name'].lower()]
        for p in process_iter():
            if p.cmdline() == cmdline: return p.pid
        return False

    def load_state(self):
        
        try:
            with open(self.state['filename'], 'rb') as f:
                self.state = loads(f.read())
        except FileNotFoundError: self.set_initial_state(self.name,self.configuration)
        except (Exception) as e: print(str(e))

    def save_state(self):

        try:
            with open(self.state['filename'], 'wb') as f:
                f.write(dumps(self.state))
        except (Exception) as e: print(str(e))

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
            self.load_state()
            print(self.state['name']+' is running. PID={} Uptime={}'.format(str(pid),self.state['uptime']), file=sys.stderr)
            return True
        else:
            print(self.state['name']+' not running.', file=sys.stderr)
            return False


    def run(self):
    
        self.logger.log(self.state['name']+' starts. PID={}'.format(str(getpid())), 1)
        while True:
            self.load_state()
            self.state['uptime'] = int(time()) - self.state['startTime']
            self.process()
            self.save_state()
            sleep(1)

    def process(self):
        
        if self.lucky(10): self.logger.log(self.state['name']+' OK, uptime is {}.'.format(self.state['uptime']))

