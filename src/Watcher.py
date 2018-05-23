#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import sys

try:
    from time import time, sleep
    from pickle import dumps, loads
    from os import getpid

except ImportError as e:

    print(str(e), file=sys.stderr)
    print('Cannot find the module(s) listed above. Exiting.', file=sys.stderr)
    sys.exit(1)

class Watcher:

    def __init__(self, configuration):
    
        self.status = {}
        self.status['watcherStartTime'] = None
        self.status['watcherUptime'] = 0
        self.status['filename'] = configuration['watcher_status_file']

    def run(self):
        
        self.status['watcherStartTime'] = int(time())
        print('PCM Watcher starts. PID={}'.format(str(getpid())), file=sys.stderr)
        while True:
            try:
                with open(self.status['filename'], 'rb') as f:
                    self.status = loads(f.read())
                    self.status['watcherUptime'] = int(time()) - self.status['watcherStartTime']
            except (FileNotFoundError, EOFError): pass
            with open(self.status['filename'], 'wb') as f:
                f.write(dumps(self.status))
            
            sleep(1)
