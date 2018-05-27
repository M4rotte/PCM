# pylint: disable=bad-whitespace,bad-continuation,line-too-long,multiple-statements,trailing-whitespace,trailing-newlines,invalid-name,trailing-whitespace
# -*- coding: UTF-8 -*-
import sys
try:
    import SSHClient
    import Daemon
    from cryptography.hazmat.primitives.serialization import load_pem_private_key
    from cryptography.hazmat.backends import default_backend as crypto_default_backend
    from os import walk as walkdir
    from os import path
    from time import time
    import re

except ImportError as e:
    print(str(e), file=sys.stderr)
    print('Cannot find the module(s) listed above. Exiting.', file=sys.stderr)
    sys.exit(1)

class Engine(Daemon.Daemon):
    def __init__(self, configuration, logger = None, name = 'Engine'):
        super().__init__(configuration, logger, 'Engine')
    
    def createSSHClient(self):
        self.SSHClient = SSHClient.SSHClient(self.readKeyFile(self.configuration['rsa_key']), self.logger, self.configuration)
        self.SSHClient.saveKey(self.configuration['rsa_key'], self.configuration['rsa_key_pub'])
    
    def readKeyFile(self, filename):
        try:
            with open(filename, 'rb') as f:
                data = f.read()
                print('Existing key in {}'.format(filename), file=sys.stderr)
                return load_pem_private_key(data,backend=crypto_default_backend(),password=None)
        except (ValueError,FileNotFoundError,EOFError): return None

    def findFile(self, directory, regex = '.*'):
        test_re = re.compile(regex)
        ok_files = []
        for root, dirs, files in walkdir(self.configuration['host_dir']):
            for f in files:
                name = root+'/'+f
                if test_re.match(name): ok_files.append(name)
        return ok_files

    def process(self):
        """Engine main procedure."""
        hosts = []
        for f in self.findFile(self.configuration['host_dir'],r'.*\.in$'):
            print('File found: '+str(f))
            basef = path.basename(f)
            hosts.append(''.join(basef.split('.')[:-1]))
        res = self.SSHClient.execute('sleep 60',hosts)
        for h in res: print(h)
        if self.state['reportTime'] >= int(self.configuration['report_time']):
            self.logger.log(self.state['name']+' OK, uptime is {}.'.format(str(int(self.state['uptime']))))
            self.state['startReportTime'] = time()

