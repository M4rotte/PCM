# pylint: disable=bad-whitespace,bad-continuation,line-too-long,multiple-statements,trailing-whitespace,trailing-newlines
"""GG
    GG Server
"""

import sys
import asyncio
from os import getpid, kill, unlink, _exit
from signal import signal, SIGTERM, SIGUSR1

class Server:

    def __init__(self, configuration, logger):
    
        print(configuration)
        print(logger)
        self.pidfile = './pcm.pid'
        self.logger = logger

    def start(self):

        self.loop = asyncio.get_event_loop()
        self.coro = asyncio.start_server(self.handle_request, '127.0.0.1', 1331, loop=self.loop)
        self.server = self.loop.run_until_complete(self.coro)
        self.logger.log('Serving on {}'.format(self.server.sockets[0].getsockname()),0)
        with open(self.pidfile,'w') as f: f.write(str(getpid()))
        signal(SIGUSR1, self.close_server)
        self.loop.run_forever()

    def stop(self):
        try:
            with open(self.pidfile,'r') as f: pid = int(f.readline())
            kill(pid,SIGUSR1)
            unlink(self.pidfile)
        except AttributeError: pass
        
    def close_server(self, signum, frame):
        self.logger.log('PID '+str(getpid())+' received signal '+str(signum)+' ('+str(frame)+')', 0)
        self.server.close()
        self.loop.run_until_complete(server.wait_closed())
        self.loop.close()
                
    @asyncio.coroutine
    def handle_request(self, reader, writer):
        data = yield from reader.read(1024)
        message = data.decode()
        addr = writer.get_extra_info('peername')
        self.logger.log("Received %r from %r" % (message, addr),0)
        
        self.logger.log("Send: %r" % message, 0)
        writer.write(data)
        yield from writer.drain()
        writer.close()



