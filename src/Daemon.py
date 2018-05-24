#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import sys

try:
    
    from random import randint
    from time import time, sleep
    from pickle import dumps, loads
    from os import getpid, kill, unlink
    from signal import signal, SIGTERM, SIGHUP

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
        self.state['filename'] = self.configuration[name.lower()+'_status_file']
        self.state['PIDfile'] = self.configuration[name.lower()+'_pid_file']

    def lucky(self, possible):
        
        if randint(1, possible) == 1: return True
        else: return False

    def start(self):
        
        if self.status(): return False
        with open(self.state['PIDfile'],'w') as f: f.write(str(getpid()))
        print(self.state['name']+' starts. PID={}'.format(str(getpid())), file=sys.stderr)

    def stop(self):
        try:
            with open(self.state['PIDfile'],'r') as f: pid = int(f.readline())
            kill(pid,SIGTERM)
            unlink(self.state['PIDfile'])
            unlink(self.state['filename'])
            self.logger.log(self.state['name']+' PID='+str(pid)+' is stopped.', 1)
            print(self.state['name']+' stopped.', file=sys.stderr)
        except (AttributeError, ProcessLookupError, FileNotFoundError): #TODO: Handle each exception individually
            print(self.state['name']+' not running.', file=sys.stderr)

    def status(self):
        try:
            with open(self.state['PIDfile'],'r') as f: pid = int(f.readline())
            with open(self.state['filename'],'rb') as f: self.state = loads(f.read())   
            print(self.state['name']+' is running. PID={} Uptime={}'.format(str(pid),str(self.state['uptime'])), file=sys.stderr)
            return True
        except (AttributeError,OSError,ValueError) as err:
            try:
                if err.errno == errno.EPERM:
                    print(self.state['name']+' is running but access is denied. PID='+str(pid), file=sys.stderr)
                    return False
                else: print(str(err), file=sys.stderr)
                return False
            except (NameError,AttributeError) as ne:
                print(self.state['name']+' not running.', file=sys.stderr)
                return False

        except EOFError:
            
            print('PCM '+self.state['name']+' is running. PID={}'.format(str(pid)), file=sys.stderr)

    def run(self):
    
        self.state['startTime'] = int(time())
        print('PCM '+self.state['name']+' starts. PID={}'.format(str(getpid())), file=sys.stderr)
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

