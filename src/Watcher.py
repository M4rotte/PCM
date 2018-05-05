#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from time import time, sleep

class Watcher:

    def __init__(self):
    
        self.start_time = int(time())
        self.uptime = 0

    def run(self):
        while True:
            self.uptime = int(time()) - self.start_time
            print('watching since: '+str(self.uptime))
            sleep(3)
