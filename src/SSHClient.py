#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import sys

try:
    
    from os import chmod
    from cryptography.hazmat.primitives import serialization as crypto_serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.backends import default_backend as crypto_default_backend
    from hashlib import blake2b

except ImportError as e:

    print(str(e), file=sys.stderr)
    print('Cannot find the module(s) listed above. Exiting.', file=sys.stderr)
    sys.exit(1)
    
class SSHClient:

    def __init__(self, key = None, logger = None):

        if not key: self.newkey()
        else:
            self.key = key
        message = 'Using key "{}"'.format(self.keyhash())
        print(message, file=sys.stderr)
        logger.log(message, 1)

    def newkey(self):

        print('Generating new key…', file=sys.stderr)
        self.key = rsa.generate_private_key(backend=crypto_default_backend(),public_exponent=65537,key_size=2048)

    def pubkey(self):
        
        return self.key.public_key().public_bytes(crypto_serialization.Encoding.OpenSSH,crypto_serialization.PublicFormat.OpenSSH)

    def privkey(self):
        
        return self.key.private_bytes(crypto_serialization.Encoding.PEM,crypto_serialization.PrivateFormat.TraditionalOpenSSL,crypto_serialization.NoEncryption())

    def saveKey(self, keyfile, pubkeyfile):

        try:
            with open(keyfile, 'wb') as f: f.write(self.privkey())
            chmod(keyfile,0o600)
        except AttributeError as e: print(str(e))

        try:
            with open(pubkeyfile, 'wb') as f: f.write(self.pubkey())
        except AttributeError as e: print(str(e))

    def keyhash(self):
        
        h = blake2b()
        h.update(self.pubkey())
        return h.hexdigest()
