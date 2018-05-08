#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import sys

try:

    from cryptography.hazmat.primitives import serialization as crypto_serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.backends import default_backend as crypto_default_backend

except ImportError as e:

    print(str(e), file=sys.stderr)
    print('Cannot find the module(s) listed above. Exiting.', file=sys.stderr)
    sys.exit(1)
    
class SSHClient:

    def __init__(self, private_key = None):

        if not private_key: self.newkey()
        else: self.private_key = private_key

    def newkey(self):

        self.private_key = rsa.generate_private_key(backend=crypto_default_backend(),public_exponent=65537,key_size=2048)

    def saveKey(self, filename):

        try:
            self.private_ssh_key = self.private_key.private_bytes(crypto_serialization.Encoding.PEM,crypto_serialization.PrivateFormat.PKCS8,crypto_serialization.NoEncryption())
            with open(filename, 'wb') as f: f.write(self.private_ssh_key)
        except AttributeError as e: print(str(e))


