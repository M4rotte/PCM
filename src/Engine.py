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
    from time import time, sleep
    import re
    from hashlib import blake2b

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

    def execOnHosts(self, cmdline):

        hosts = []
        for f in self.findFile(self.configuration['host_dir'],r'.*\.in$'):
            basef = path.basename(f)
            hosts.append(''.join(basef.split('.')[:-1]))
        if len(hosts) > 0:
            self.state['hosts'] = hosts
            return self.SSHClient.execute(cmdline, hosts)
        else:
            self.logger.log('Host directory "'+self.configuration['host_dir']+'" has no host input files (*.in), nothing to do!', 1)
            return False

    def scriptKnownHash(self, hostname, scriptname):
        
        try:
            return self.state['hash_'+hostname+'_'+scriptname]
        except KeyError:
            blakesum = blake2b()
            blakesum.update(open(self.configuration['script_dir']+'/'+scriptname,'rb').read())
            self.state['hash_'+hostname+'_'+scriptname] = blakesum.hexdigest()
            return False
    
    def scriptCurrentHash(self, hostname, scriptname):
        
        try:
            blakesum = blake2b()
            blakesum.update(open(self.configuration['script_dir']+'/'+scriptname,'rb').read())
            return blakesum.hexdigest()
        except FileNotFoundError:
            return False
       
    def scriptChangedOrNew(self, hostname, scriptname):
        
        return self.scriptKnownHash(hostname, scriptname) != self.scriptCurrentHash(hostname, scriptname)
       
    def checkHost(self, hostname):
        
        self.genScripts(hostname)

    def genScripts(self, hostname):

        try:
            with open(self.configuration['host_dir']+'/'+hostname+'.in', 'r') as hf:
                for line in hf:
                    line = line.strip()
                    if not line: continue
                    if not self.scriptChangedOrNew(hostname, line):
                        self.logger.log('Script "{}" for host "{}" unchanged.'.format(line, hostname), 0)
                        continue
                    outfilename = self.configuration['script_dir']+'/'+hostname+'_'+line+'.sh'
                    self.logger.log('Generating script "{}" for host "{}" in "{}"'.format(line,hostname,outfilename), 0)
                    with open(outfilename,'w') as f:
                        infilename = self.configuration['script_dir']+'/'+line
                        f.write('#!/bin/sh\n')
                        exec(open(infilename).read())
        except Exception as e: print(str(e))

    def process(self):
        """Engine main procedure."""
        print(self.execOnHosts('ls'))
        self.checkHost('opium')
        self.report()
        sleep(10)

