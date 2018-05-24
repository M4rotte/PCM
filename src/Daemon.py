#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import sys

try:
    
    from random import randint
    from time import time, sleep
    from pickle import dumps, loads
    from os import getpid

except ImportError as e:

    print(str(e), file=sys.stderr)
    print('Cannot find the module(s) listed above. Exiting.', file=sys.stderr)
    sys.exit(1)

class Daemon:

    def __init__(self, configuration, logger, name):
        
        self.status = {}
        self.logger = logger
        self.status['name'] = name
        self.status['startTime'] = None
        self.status['uptime'] = 0
        self.status['filename'] = configuration[name.lower()+'_status_file']
        print('PCM '+self.status['name']+' starts. PID={}'.format(str(getpid())), file=sys.stderr)

    def lucky(self, possible = 1):
        
        # ~ if possible.is_integer(): possible = abs(possible)
        # ~ else: possible = 1
        if randint(1, possible) == 1: return True
        else: return False

    def run(self):
    
        self.status['startTime'] = int(time())
        print('PCM '+self.status['name']+' starts. PID={}'.format(str(getpid())), file=sys.stderr)
        self.logger.log('PCM '+self.status['name']+' starts. PID={}'.format(str(getpid())), 0)
        while True:
            try:
                with open(self.status['filename'], 'rb') as f:
                    self.status = loads(f.read())
                    self.status['uptime'] = int(time()) - self.status['startTime']
            except (FileNotFoundError, EOFError): pass
            with open(self.status['filename'], 'wb') as f:
                f.write(dumps(self.status))
            self.process()
            sleep(1)

    def process(self):
        
        if self.lucky(10): self.logger.log(self.status['name']+' OK, uptime is {}.'.format(self.status['uptime']))
