#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import sys

try:

    import Daemon

except ImportError as e:

    print(str(e), file=sys.stderr)
    print('Cannot find the module(s) listed above. Exiting.', file=sys.stderr)
    sys.exit(1)

class Watcher(Daemon.Daemon):

    def __init__(self, configuration, logger = None):

        super().__init__(configuration, logger, 'Watcher')


