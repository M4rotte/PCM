# pylint: disable=bad-whitespace,bad-continuation,line-too-long,multiple-statements,trailing-whitespace,trailing-newlines,invalid-name,trailing-whitespace
# -*- coding: UTF-8 -*-
"""PCM Listener."""
import sys
import asyncio
from os import getpid, _exit
from signal import signal, SIGUSR1, SIGHUP
from psutil import Process
from time import time
from datetime import timedelta
import Daemon

class Listener(Daemon.Daemon):
    """The Listener object subclasses Daemon, but unlike other classes which subclass it, 
        it even overrides its start() method, thus making it behave differently:
        The process() method is never called, so except of handling requests, the corresponding 
        process do nothing else. The report() method can’t be called either."""
    def __init__(self, configuration, logger = None, name = 'Listener'):
        super().__init__(configuration, logger, 'Listener')

    def start(self):
        """Start the listener process."""
        print('Listener starts. PID={}'.format(str(getpid())), file=sys.stderr)
        try:
            self.loop = asyncio.get_event_loop()
            self.coro = asyncio.start_server(self.handle_request, '127.0.0.1', 1331, loop=self.loop)
            self.server = self.loop.run_until_complete(self.coro)
            self.logger.log('Serving on {}'.format(self.server.sockets[0].getsockname()),0)
            signal(SIGUSR1, self.close_server)
            self.save_state()
            message = 'Listening on {}. PID={}'.format(self.server.sockets[0].getsockname(),getpid())
            print(message, file=sys.stderr)
            self.logger.log(message, 1)
            self.configuration['name'] = 'Listener'
            self.loop.run_forever()
        except OSError as err:
            print(str(err), file=sys.stderr)

    # Due to how start() is overridden, the following can’t be used:
    def process(): pass
    def report(): pass

    def close_server(self, signum, frame):
        self.logger.log('Server PID='+str(getpid())+' received signal '+str(signum)+' ('+str(frame)+'). Stopping…', 1)
        self.loop.stop()
        self.server.close()
        _exit(0)

    def process_request(self,request):
        if request.strip() == 'uptime':
            seconds = int(time() - Process(getpid()).create_time())
            response = str(timedelta(seconds=seconds))
        elif request.strip() == 'config':
            response = self.config()
        else: response = ''
        return response

    @asyncio.coroutine
    def handle_request(self, reader, writer):
        data = yield from reader.read(1024)
        message = data.decode()
        addr = writer.get_extra_info('peername')
        self.logger.log("Received %r from %r" % (message, addr),0)
        response = self.process_request(message)+'\n'
        self.logger.log("Send: %r to %r" % (response, addr), 0)
        writer.write(response.encode('utf-8'))
        yield from writer.drain()
        writer.close()



