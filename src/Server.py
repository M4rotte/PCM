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
        self.status = {}
        self.status['serverStartTime'] = None
        self.status['serverUptime'] = 0
        self.status['filename'] = configuration['server_status_file']

    def start(self):

        if self.serverStatus(): return False

        try:
            self.loop = asyncio.get_event_loop()
            self.coro = asyncio.start_server(self.handle_request, '127.0.0.1', 1331, loop=self.loop)
            self.server = self.loop.run_until_complete(self.coro)
            self.logger.log('Serving on {}'.format(self.server.sockets[0].getsockname()),0)
            self.status['serverStartTime'] = int(time())
            with open(self.pidfile,'w') as f: f.write(str(getpid()))
            with open(self.status['filename'] , 'wb') as f:
                f.write(dumps(self.status))
            signal(SIGUSR1, self.close_server)
            print('PCM server is listening on {}. PID={}'.format(self.server.sockets[0].getsockname(),getpid()), file=sys.stderr)
            self.loop.run_forever()
        except OSError as err:
            print(str(err), file=sys.stderr)

    def stop(self):
        try:
            with open(self.pidfile,'r') as f: pid = int(f.readline())
            kill(pid,SIGUSR1)
            unlink(self.pidfile)
            unlink(self.status['filename'])
            print('PCM Server  stopped.', file=sys.stderr)
        except (AttributeError,FileNotFoundError): 
            print('PCM Server  not running.', file=sys.stderr)
 
    def serverStatus(self):
        try:
            with open(self.pidfile,'r') as f: pid = int(f.readline())
            try:
                with open(self.status['filename'], 'rb') as f:
                    self.status = loads(f.read())
                    self.status['serverUptime'] = int(time()) - self.status['serverStartTime']
            except (FileNotFoundError, EOFError): pass
            with open(self.status['filename'], 'wb') as f:
                f.write(dumps(self.status))
            print('PCM Server is running. PID={} Uptime={}'.format(str(pid), str(self.status['serverUptime'])), file=sys.stderr)
            return True
        except (AttributeError,OSError) as err:
            try:
                if err.errno == errno.EPERM:
                    print('PCM Server is running but access is denied. PID='+str(pid), file=sys.stderr)
                    return False
                else: print(str(err), file=sys.stderr)
                return False
            except NameError as ne:
                print('No PID file found for PCM Server. '+str(err), file=sys.stderr)
                return False
        
    def close_server(self, signum, frame):
        self.logger.log('PCM Server PID='+str(getpid())+' received signal '+str(signum)+' ('+str(frame)+'). Stopping…', 0)
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



