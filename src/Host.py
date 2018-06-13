# pylint: disable=bad-whitespace,bad-continuation,line-too-long,multiple-statements,trailing-whitespace,trailing-newlines,invalid-name,trailing-whitespace
# -*- coding: UTF-8 -*-
import sys
try:

    from os import walk as walkdir
    from os import path
    from random import randint

except ImportError as e:
    print(str(e), file=sys.stderr)
    print('Cannot find the module(s) listed above. Exiting.', file=sys.stderr)
    sys.exit(1)

class Host:

    def __init__(self, hostname, configuration, logger):
    
        self.configuration = configuration
        self.logger = logger
        self.name = hostname
        self.entrypoint = self.configuration['host_dir']+'/'+hostname+'/'+self.configuration['entry_point']

    def __str__(self):
        
        return self.name

    def Process(self):
        
        def R(ressource):
        
            try:
                rfn = self.configuration['host_dir']+'/'+self.name+'/'+self.configuration['ressource_dir']+'/'+ressource
                with open(rfn) as f:
                    loc = {}
                    available_builtins  = {'locals': locals,
                                           'globals': globals,
                                           'print': print,
                                           'randint': randint}
                    exec(f.read(), {'__builtins__': available_builtins}, loc)
                    self.logger.log('Ressource “'+ressource+'” processed. ('+rfn+')', 0)
                    return loc['state']
                    
            except FileNotFoundError:
                self.logger.log('Ressource “'+ressource+'” not found.("'+rfn+'" not found)', 1)
                return 'NotFound'
            
            except Exception as err:
                self.logger.log('Ressource “'+ressource+'” is invalid. ('+str(err)+')', 2)
                return 'Invalid'
        
        try:
            with open(self.entrypoint,'r') as f:
                self.logger.log('Processing '+self.configuration['entry_point'], 0)
                self.state = exec(f.read())
                self.logger.log(self.configuration['entry_point']+' processed.', 0)
                return self.state
        except FileNotFoundError:
            self.logger.log('Host “'+self.name+'” has no entry point. ("'+self.entrypoint+'" not found)', 1)
            return 'Unprocessed'
        except Exception:
            self.logger.log('`'+self.entrypoint+'` is invalid!', 2)
            return 'Unprocessed'

