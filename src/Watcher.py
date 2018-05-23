#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import sys

try:
    from time import time, sleep
    from pickle import dumps, loads
    from os import getpid
    import Daemon

except ImportError as e:

    print(str(e), file=sys.stderr)
    print('Cannot find the module(s) listed above. Exiting.', file=sys.stderr)
    sys.exit(1)

class Watcher(Daemon.Daemon):

    def __init__(self, configuration, logger):
    
        super().__init__(configuration, logger)
        self.status['watcherStartTime'] = None
        self.status['watcherUptime'] = 0
        self.status['filename'] = configuration['watcher_status_file']

    def run(self):
        
        self.status['watcherStartTime'] = int(time())
        print('PCM Watcher starts. PID={}'.format(str(getpid())), file=sys.stderr)
        self.logger.log('PCM Watcher starts. PID={}'.format(str(getpid())), 0)
        while True:
            try:
                with open(self.status['filename'], 'rb') as f:
                    self.status = loads(f.read())
                    self.status['watcherUptime'] = int(time()) - self.status['watcherStartTime']
            except (FileNotFoundError, EOFError): pass
            with open(self.status['filename'], 'wb') as f:
                f.write(dumps(self.status))
            if self.lucky(10): self.logger.log('Watcher OK, uptime is {}.'.format(self.status['watcherUptime']))
            sleep(1)

    def process(self):
        
        pass
