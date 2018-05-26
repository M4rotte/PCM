# pylint: disable=bad-whitespace,bad-continuation,line-too-long,multiple-statements,trailing-whitespace,trailing-newlines,invalid-name,trailing-whitespace
# -*- coding: UTF-8 -*-
"""PCM Watcher."""
import sys
try:
    import Daemon
except ImportError as e:
    print(str(e), file=sys.stderr)
    print('Cannot find the module(s) listed above. Exiting.', file=sys.stderr)
    sys.exit(1)

class Watcher(Daemon.Daemon):
    def __init__(self, configuration, logger = None, name = 'Watcher'):
        super().__init__(configuration, logger, 'Watcher')


