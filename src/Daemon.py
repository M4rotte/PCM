#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import sys

try:
    from random import randint

except ImportError as e:

    print(str(e), file=sys.stderr)
    print('Cannot find the module(s) listed above. Exiting.', file=sys.stderr)
    sys.exit(1)

class Daemon:

    def __init__(self, configuration, logger, name):
        
        self.status = {}
        self.logger = logger
        self.status['startTime'] = None
        self.status['uptime'] = 0

    def lucky(self, nb_possible = 1):
    
        if randint(1, abs(nb_possible)) == 1: return True
        else: return False
    
    
