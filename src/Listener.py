# pylint: disable=bad-whitespace,bad-continuation,line-too-long,multiple-statements,trailing-whitespace,trailing-newlines
"""PCM
    PCM Listener
"""

import sys
import asyncio
from os import getpid, kill, unlink, _exit, path
from signal import signal, SIGTERM, SIGUSR1
from time import sleep, time
from pickle import dumps,loads
from psutil import process_iter

import PCM

class Listener:

    def __init__(self, configuration, logger):
    
        self.logger = logger
        self.state = {}
        self.state['startTime'] = None
        self.state['uptime'] = 0
        self.state['filename'] = configuration['pcm_dir']+'/'+'listener.state'

    def process_exists(self):
                
        cmdline = [path.basename(sys.executable),sys.argv[0],'listener']
        for p in process_iter():
            if p.cmdline() == cmdline: return p.pid
        return False

    def start(self):

        print('Listener starts. PID={}'.format(str(getpid())), file=sys.stderr)
        
        try:
            self.loop = asyncio.get_event_loop()
            self.coro = asyncio.start_server(self.handle_request, '127.0.0.1', 1331, loop=self.loop)
            self.server = self.loop.run_until_complete(self.coro)
            self.logger.log('Serving on {}'.format(self.server.sockets[0].getsockname()),0)
            self.state['startTime'] = int(time())
            with open(self.state['filename'] , 'wb') as f:
                f.write(dumps(self.state))
            signal(SIGUSR1, self.close_server)
            message = 'Listening on {}. PID={}'.format(self.server.sockets[0].getsockname(),getpid())
            print(message, file=sys.stderr)
            self.logger.log(message, 1)
            self.loop.run_forever()
            
        except OSError as err:
            print(str(err), file=sys.stderr)

    def stop(self):
        
        pid = self.process_exists()
        
        if pid:
            kill(pid,SIGTERM)
            unlink(self.state['filename'])
            print('Listener stopped.', file=sys.stderr)
            self.logger.log('Listener PID='+str(pid)+' stopped.', 1)
            return True
        else:
            print('Listener is not running.', file=sys.stderr)
            return False
 
    def status(self):
        
        pid = self.process_exists()
        
        if pid:
            print('Listener is running. PID={}'.format(str(pid)), file=sys.stderr)
            return True
        else:
            print('Listener is not running.', file=sys.stderr)
            return False
        
    def close_server(self, signum, frame):
        self.logger.log('Server PID='+str(getpid())+' received signal '+str(signum)+' ('+str(frame)+'). Stopping…', 1)
        self.loop.stop()
        self.server.close()
        _exit(0)

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



