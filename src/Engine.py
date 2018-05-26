# pylint: disable=bad-whitespace,bad-continuation,line-too-long,multiple-statements,trailing-whitespace,trailing-newlines,invalid-name,trailing-whitespace
# -*- coding: UTF-8 -*-
import sys
try:
    import SSHClient
    import Daemon
    from cryptography.hazmat.primitives.serialization import load_pem_private_key
    from cryptography.hazmat.backends import default_backend as crypto_default_backend

except ImportError as e:
    print(str(e), file=sys.stderr)
    print('Cannot find the module(s) listed above. Exiting.', file=sys.stderr)
    sys.exit(1)

class Engine(Daemon.Daemon):
    def __init__(self, configuration, logger = None, name = 'Engine'):
        super().__init__(configuration, logger, 'Engine')
    
    def createSSHClient(self):
        self.SSHClient = SSHClient.SSHClient(self.readKeyFile(self.configuration['rsa_key']), self.logger)
        self.SSHClient.saveKey(self.configuration['rsa_key'], self.configuration['rsa_key_pub'])
    
    def readKeyFile(self, filename):
        try:
            with open(filename, 'rb') as f:
                data = f.read()
                print('Existing key in {}'.format(filename), file=sys.stderr)
                return load_pem_private_key(data,backend=crypto_default_backend(),password=None)
        except (ValueError,FileNotFoundError,EOFError): return None
        


