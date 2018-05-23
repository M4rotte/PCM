#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import sys

try:

    import SSHClient
    from cryptography.hazmat.primitives.serialization import load_pem_private_key
    from cryptography.hazmat.backends import default_backend as crypto_default_backend

except ImportError as e:

    print(str(e), file=sys.stderr)
    print('Cannot find the module(s) listed above. Exiting.', file=sys.stderr)
    sys.exit(1)

class Engine:

    def __init__(self, configuration):
    
       print('\nCreating engine using {} as key file.'.format(configuration['rsa_key']))
       self.SSHClient = SSHClient.SSHClient(self.readKeyFile(configuration['rsa_key']))
       self.SSHClient.saveKey(configuration['rsa_key'])
    
    def readKeyFile(self, filename):
        
        try:
            with open(filename, 'rb') as f:
                data = f.read()
                return load_pem_private_key(data,backend=crypto_default_backend(),password=None)
        except (ValueError,FileNotFoundError,EOFError): return None
        
    def run(self):
    
        pass
        
