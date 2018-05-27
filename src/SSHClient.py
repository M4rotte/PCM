# pylint: disable=bad-whitespace,bad-continuation,line-too-long,multiple-statements,trailing-whitespace,trailing-newlines,invalid-name,trailing-whitespace
# -*- coding: UTF-8 -*-
"""PCM SSH client."""
import sys
try:
    from os import chmod
    from multiprocessing import Process, Queue
    from cryptography.hazmat.primitives import serialization as crypto_serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.backends import default_backend as crypto_default_backend
    from hashlib import blake2b
    from signal import SIGALRM
    from time import time
    import paramiko
    from socket import timeout
    from io import StringIO
    import signal
except ImportError as e:
    print(str(e), file=sys.stderr)
    print('Cannot find the module(s) listed above. Exiting.', file=sys.stderr)
    sys.exit(1)

def handleSignal(signum, frame):
    
    if signum == SIGALRM: raise WithdrawException('Execution left unsupervised')
    else: raise Exception('Signal: '+str(signum)+' at: '+str(frame))

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n): yield l[i:i + n]

class WithdrawException(Exception):
    
    def __init__(self, message): super().__init__(message)

class SSHClient:
    """SSH client makes all SSH related actions."""
    def __init__(self, key = None, logger = None, configuration = None):
        """The SSH client is initialized with the given RSA key. A new key is generated if none is given."""
        self.configuration = configuration
        if not key: self.newkey()
        else: self.key = key
        message = 'Using key "{}"'.format(self.keyhash())
        print(message, file=sys.stderr)
        self.logger = logger
        logger.log(message, 1)
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.load_system_host_keys()

    def newkey(self):
        """Generate a RSA key."""
        print('Generating new key…', file=sys.stderr)
        self.key = rsa.generate_private_key(backend=crypto_default_backend(),public_exponent=65537,key_size=2048)

    def pubkey(self):
        """Return the public key."""
        return self.key.public_key().public_bytes(crypto_serialization.Encoding.OpenSSH,crypto_serialization.PublicFormat.OpenSSH)

    def privkey(self):
        """Return the private key."""
        return self.key.private_bytes(crypto_serialization.Encoding.PEM,crypto_serialization.PrivateFormat.TraditionalOpenSSL,crypto_serialization.NoEncryption())

    def sshkey(self):
        k = paramiko.RSAKey.from_private_key(StringIO(self.privkey().decode('utf-8')),password=None)
        return k

    def saveKey(self, keyfile, pubkeyfile):
        """Write the key pair to files."""
        try:
            with open(keyfile, 'wb') as f: f.write(self.privkey())
            chmod(keyfile,0o600)
        except AttributeError as e: print(str(e))
        try:
            with open(pubkeyfile, 'wb') as f: f.write(self.pubkey())
        except AttributeError as e: print(str(e))

    def keyhash(self):
        """Return public key’s fingerprint."""
        h = blake2b()
        h.update(self.pubkey())
        return h.hexdigest()

    def _execute(self, host, cmdline, q):
        """Execute a command on a host and put the result in a queue."""
        start  = time()
        try:
            exec_status = ''
            return_code = 0
            self.client.connect(host, username=self.configuration['pcm_user'], pkey=self.sshkey(), timeout=float(self.configuration['client_timeout']),
                                banner_timeout=float(self.configuration['banner_timeout']), auth_timeout=float(self.configuration['auth_timeout']))
            std    = self.client.exec_command(cmdline, timeout=float(self.configuration['exec_timeout']))
            signal.alarm(int(self.configuration['exec_timeout']))
            signal.signal(signal.SIGALRM, handleSignal)
            return_code = std[1].channel.recv_exit_status()
            stdout = list(std[1])
            stderr = list(std[2])
            end    = time()
            q.put((self.configuration['pcm_user'], host, cmdline, return_code, stdout, stderr, exec_status, start, end))
            self.client.close()

        except (paramiko.ssh_exception.AuthenticationException,
                paramiko.ssh_exception.NoValidConnectionsError,
                paramiko.ssh_exception.SSHException,
                timeout,OSError,EOFError,ConnectionResetError,AttributeError) as error:
            end = time()
            self.logger.log(str(error),3)
            q.put((self.configuration['pcm_user'], host, cmdline, -1, [], [], str(error), start, end))
            self.client.close()
            return False
            
        except WithdrawException as error:

            end = time()
            self.logger.log(str(error),3)
            q.put((self.configuration['pcm_user'], host, cmdline, -1, [], [], str(error), start, end))
            self.client.close()
            return False  

        return True

    def execute(self, cmdline, hosts):
        """Execute a command on hosts in parallel."""
        q = Queue()
        runs = []
        processes = []
        try: chunk_size = int(self.configuration['host_chunk_size'])
        except KeyError: chunk_size = 4
        self.logger.log('Executing `'+cmdline+'` on '+str(len(hosts))+' hosts in chunks of '+str(chunk_size)+' hosts.',0)
        for chunk in chunks(hosts, chunk_size):
            nb_hosts = len(chunk)
            for host in chunk:
                proc = Process(target=self._execute, args=(host, cmdline, q))
                proc.start()
                processes.append(proc)
            for p in processes: p.join()
            for _ in range(0, nb_hosts):
                runs.append(q.get())

        return runs
