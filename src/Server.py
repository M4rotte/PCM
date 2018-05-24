# pylint: disable=bad-whitespace,bad-continuation,line-too-long,multiple-statements,trailing-whitespace,trailing-newlines
"""PCM
    PCM Server
"""

import sys
import asyncio
from os import getpid, kill, unlink, _exit
from signal import signal, SIGTERM, SIGUSR1
from time import sleep, time
from pickle import dumps,loads

import PCM

class Server:

    def __init__(self, configuration, logger):
    
        self.pidfile = configuration['server_pid_file']
        self.logger = logger
        self.state = {}
        self.state['startTime'] = None
        self.state['uptime'] = 0
        self.state['filename'] = configuration['server_state_file']

    def start(self):

        if self.status(): return False
        print('Server starts. PID={}'.format(str(getpid())), file=sys.stderr)
        try:
            self.loop = asyncio.get_event_loop()
            self.coro = asyncio.start_server(self.handle_request, '127.0.0.1', 1331, loop=self.loop)
            self.server = self.loop.run_until_complete(self.coro)
            self.logger.log('Serving on {}'.format(self.server.sockets[0].getsockname()),0)
            self.state['serverStartTime'] = int(time())
            with open(self.pidfile,'w') as f: f.write(str(getpid()))
            with open(self.state['filename'] , 'wb') as f:
                f.write(dumps(self.state))
            signal(SIGUSR1, self.close_server)
            message = 'Server is listening on {}. PID={}'.format(self.server.sockets[0].getsockname(),getpid())
            print(message, file=sys.stderr)
            self.logger.log(message, 1)
            self.loop.run_forever()
        except OSError as err:
            print(str(err), file=sys.stderr)

    def stop(self):
        try:
            with open(self.pidfile,'r') as f: pid = int(f.readline())
            kill(pid,SIGUSR1)
            unlink(self.pidfile)
            unlink(self.state['filename'])
            print('Server stopped.', file=sys.stderr)
        except (AttributeError,FileNotFoundError,ProcessLookupError): 
            print('Server not running.', file=sys.stderr)
 
    def status(self):
        try:
            with open(self.pidfile,'r') as f: pid = int(f.readline())
            try:
                with open(self.state['filename'], 'rb') as f:
                    self.state = loads(f.read())
                    self.state['serverUptime'] = int(time()) - self.state['serverStartTime']
            except (FileNotFoundError, EOFError): pass
            with open(self.state['filename'], 'wb') as f:
                f.write(dumps(self.state))
            print('Server is running. PID={} Uptime={}'.format(str(pid), str(self.state['serverUptime'])), file=sys.stderr)
            return True
        except (AttributeError,OSError) as err:
            try:
                if err.errno == errno.EPERM:
                    print('Server is running but access is denied. PID='+str(pid), file=sys.stderr)
                    return False
                else: print(str(err), file=sys.stderr)
                return False
            except NameError as ne:
                print('Server not running.', file=sys.stderr)
                return False
        
    def close_server(self, signum, frame):
        self.logger.log('Server PID='+str(getpid())+' received signal '+str(signum)+' ('+str(frame)+'). Stopping…', 1)
        self.server.close()
        self.loop.run_until_complete(server.wait_closed())
        self.loop.close()

    def process_request(self,request):

        return request

    @asyncio.coroutine
    def handle_request(self, reader, writer):
        data = yield from reader.read(1024)
        message = data.decode()
        addr = writer.get_extra_info('peername')
        self.logger.log("Received %r from %r" % (message, addr),0)
        response = self.process_request(message)
        self.logger.log("Send: %r to %r" % (response, addr), 0)
        writer.write(data)
        yield from writer.drain()
        writer.close()



