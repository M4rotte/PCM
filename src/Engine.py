# pylint: disable=bad-whitespace,bad-continuation,line-too-long,multiple-statements,trailing-whitespace,trailing-newlines,invalid-name,trailing-whitespace
# -*- coding: UTF-8 -*-
import sys
try:
    import SSHClient
    import Daemon
    import Host
    from cryptography.hazmat.primitives.serialization import load_pem_private_key
    from cryptography.hazmat.backends import default_backend as crypto_default_backend
    from os import walk as walkdir
    from os import path
    from time import time, sleep, strftime
    from hashlib import blake2b
    import re

except ImportError as e:
    print(str(e), file=sys.stderr)
    print('Cannot find the module(s) listed above. Exiting.', file=sys.stderr)
    sys.exit(1)

class Engine(Daemon.Daemon):
    def __init__(self, configuration, logger = None, name = 'Engine'):
        super().__init__(configuration, logger, 'Engine')
        self.re_script = re.compile(r'^.*\.sh$')
    
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

    def getHosts(self): return next(walkdir(self.configuration['host_dir']))[1]

    def getScripts(self, hostname):
        
        scripts = []
        for f in next(walkdir(self.configuration['host_dir']+'/'+hostname+'/'))[2]:
            if self.re_script.match(f):
                scripts.append('.'.join(f.split('.')[:-1]))
        return scripts
        

    def execOnHosts(self, cmdline):

        hosts = self.getHosts()
        if len(hosts) > 0:
            self.state['hosts'] = hosts
            return self.SSHClient.execute(cmdline, hosts)
        else:
            self.logger.log('No host defined in "'+self.configuration['host_dir']+'"', 1)
            return False

    def execScripts(self, user, hostname, scripts):

        try:
            return self.SSHClient.executeScripts(hostname, scripts)
        except Exception as e:
            print(str(e))

    def scriptHash(self, scriptname):
        """Compute the hash of the script."""
        blakesum = blake2b()
        blakesum.update(open(self.configuration['script_dir']+'/'+scriptname,'rb').read())
        return blakesum.hexdigest()

    def scriptDiffers(self, hostname, scriptname):
        """Return True if the current script’s hash differs from the one saved in the state file for this host, and save this current hash."""
        try:
            currenthash = self.scriptHash(scriptname)
            knownhash = self.state['hash_'+hostname+'_'+scriptname]
            self.state['hash_'+hostname+'_'+scriptname] = currenthash
            return knownhash != currenthash
        except KeyError:
            self.state['hash_'+hostname+'_'+scriptname] = currenthash
            return True
        return True

    def processHost(self, hostname):
        
        host = Host.Host(hostname, self.configuration, self.logger)
        return host.Process()

    def checkHost(self, hostname):
        
        self.genScripts(hostname)
        self.processHost(hostname)

    def genScripts(self, hostname):
        """Generate the scripts for a given host."""
        try:
            with open(self.configuration['host_dir']+'/'+hostname+'/scripts', 'r') as script_file:
                for line in script_file:
                    line = line.strip()
                    if not line: continue
                    if not self.scriptDiffers(hostname, line):
                        self.logger.log('Script "{}" for host "{}" unchanged.'.format(line, hostname), 0)
                        continue
                    outfilename = self.configuration['host_dir']+'/'+hostname+'/'+line+'.sh'
                    self.logger.log('Generating script "{}" for host "{}" in "{}"'.format(line,hostname,outfilename), 0)
                    with open(outfilename,'w') as output:
                        infilename = self.configuration['script_dir']+'/'+line
                        output.write('#!/bin/sh\n')
                        output.write('# Script: {} | Host: {} | Time: {}\n\n'.format(line,hostname,strftime("%Y-%m-%d %H:%M:%S %Z")))
                        exec(open(infilename).read())
        except FileNotFoundError: pass
        except Exception as e: print(str(e))

    def execHostScripts(self,hostname):

        return self.execScripts('root', hostname, self.getScripts(hostname))

    def process(self):
        """Engine main procedure."""
        # ~ print(self.execOnHosts('ls'))
        for host in self.getHosts():
            self.checkHost(host)
            # ~ print(self.execHostScripts(host))
        self.report()
        sleep(10)

