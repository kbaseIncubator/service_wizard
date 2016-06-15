#BEGIN_HEADER
import os
import time
import yaml
import subprocess
from  pprint import pprint, pformat
import traceback
import gdapi
import json
import zipfile
from StringIO import StringIO
import re
from urlparse import urlparse

import base64
import hashlib


from biokbase.catalog.Client import Catalog
#END_HEADER


class ServiceWizard:
    '''
    Module Name:
    ServiceWizard

    Module Description:
    
    '''

    ######## WARNING FOR GEVENT USERS #######
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    #########################################
    VERSION = "0.0.1"
    GIT_URL = "git@github.com:msneddon/service_wizard.git"
    GIT_COMMIT_HASH = "337ac08bfa22bd8b596806d7fd526e02f1241b6f"
    
    #BEGIN_CLASS_HEADER

    RANCHER_COMPOSE_BIN = 'rancher-compose'
    USE_RANCHER_ACCESS_KEY = True
    RANCHER_ACCESS_KEY = ''
    RANCHER_SECRET_KEY = ''

    CATALOG_URL = ''
    SCRATCH_DIR = ''


    def get_stack_name(self, module_version):
        return module_version['module_name'] + '-'+module_version['version'] + '-' + module_version['git_commit_hash'][:7]


    def create_compose_files2(self, module_version):

        # Use the name returned from the catalog service
        hasher = hashlib.sha1(module_version['module_name'])
        module_name_hash = base64.urlsafe_b64encode(hasher.digest())
        service_name = module_name_hash + '-' + module_version['git_commit_hash']

        shash = module_version['git_commit_hash']
        catalog_module_name = module_version['module_name']

        sname = "{0}-{1}".format(catalog_module_name,shash) # service name
        docker_compose = { 
            shash : {
                "image" : "rancher/dns-service",
                "links" : [ sname+':'+sname ]
            },
            sname : {
                "image" : module_version['docker_img_name']
            }
        }
        rancher_compose = {
            sname : {
                "scale" : 1
            }
        }
        return docker_compose, rancher_compose

    def create_compose_files(self, module_version):

        # hash the module name so we don't have to deal with illegal characters, length limits, etc
        module_name = module_version['module_name']
        git_commit_hash = module_version['git_commit_hash']
        module_name_hash = hashlib.md5(module_name).hexdigest()[:20]

        # construct the service names
        service_name = module_name_hash + '-' + git_commit_hash
        dns_service_name = git_commit_hash

        docker_compose = { 
            dns_service_name : {
                "image" : "rancher/dns-service",
                "links" : [ service_name+':'+service_name ]
            },
            service_name : {
                "image" : module_version['docker_img_name']
            }
        }
        rancher_compose = {
            service_name : {
                "scale" : 1
            }
        }
        return docker_compose, rancher_compose

    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        self.deploy_config = config
        if 'svc-hostname' not in config:
            up = urlparse(config['rancher-env-url'])
            self.deploy_config['svc-hostname'] = up.hostname
        if 'nginx-port' not in config:
            self.deploy_config['nginx-port'] = 443

        if 'rancher-compose-bin' in config:
            self.RANCHER_COMPOSE_BIN = config['rancher-compose-bin']

        if 'catalog-url' not in config:
            raise ValueError('"catalog-url" configuration variable not set"')
        self.CATALOG_URL = config['catalog-url']

        if 'temp-dir' not in config:
            raise ValueError('"temp-dir" configuration variable not set"')
        self.SCRATCH_DIR = config['temp-dir']

        if not os.path.isfile(self.RANCHER_COMPOSE_BIN):
            print('WARNING: rancher-compose (='+self.RANCHER_COMPOSE_BIN+') command not found.  Set absolute location with "rancher-compose-bin" configuration.')

        if ('access-key' not in config) or ('secret-key' not in config):
            self.USE_RANCHER_ACCESS_KEY = False
            print('WARNING: No "access-key" and "secret-key" set for Rancher.  Will connect unauthenticated, which should only be used in test environments.')
        else:
            self.RANCHER_ACCESS_KEY = config['access-key']
            self.RANCHER_SECRET_KEY = config['secret-key']
            print('here');

        #END_CONSTRUCTOR
        pass
    

    def version(self, ctx):
        """
        Get the version of the deployed service wizard endpoint.
        :returns: instance of String
        """
        # ctx is the context object
        # return variables are: version
        #BEGIN version
        version='1.0.0'
        #END version

        # At some point might do deeper type checking...
        if not isinstance(version, basestring):
            raise ValueError('Method version return value ' +
                             'version is not type basestring as required.')
        # return the results
        return [version]

    def start(self, ctx, service):
        """
        :param service: instance of type "Service" (version - unified version
           field including semantic version, git commit hash and case of last
           version of tag (dev/beta/release).) -> structure: parameter
           "module_name" of String, parameter "version" of String
        """
        # ctx is the context object
        #BEGIN start

        print('STARTING: ' + str(service))

        # First, lookup the module information from the catalog, make sure it is a service
        cc = Catalog(self.CATALOG_URL, token=ctx['token'])
        mv = cc.get_module_version({'module_name' : service['module_name'], 'version' : service['version']})
        if 'dynamic_service' not in mv:
            raise ValueError('Specified module is not marked as a dynamic service. ('+mv['module_name']+'-' + mv['git_commit_hash']+')')
        if mv['dynamic_service'] != 1:
            raise ValueError('Specified module is not marked as a dynamic service. ('+mv['module_name']+'-' + mv['git_commit_hash']+')')

        # Construct the docker compose and rancher compose file
        docker_compose, rancher_compose = self.create_compose_files(mv)

        # To do: try to use API to send docker-compose directly instead of needing to write to disk
        ymlpath = self.SCRATCH_DIR + '/' + mv['module_name'] + '/' + str(int(time.time()))
        os.makedirs(ymlpath)

        docker_compose_path=ymlpath + '/docker-compose.yml'
        rancher_compose_path=ymlpath + '/rancher-compose.yml'

        with open(docker_compose_path, 'w') as outfile:
            outfile.write( yaml.safe_dump(docker_compose, default_flow_style=False) )
        # can be extended later
        with open(rancher_compose_path, 'w') as outfile:
            outfile.write( yaml.safe_dump(rancher_compose, default_flow_style=False) )

        # setup Rancher creds and options
        eenv = os.environ.copy()
        eenv['RANCHER_URL'] = self.deploy_config['rancher-env-url']
        if self.USE_RANCHER_ACCESS_KEY:
            eenv['RANCHER_ACCESS_KEY'] = self.RANCHER_ACCESS_KEY
            eenv['RANCHER_SECRET_KEY'] = self.RANCHER_SECRET_KEY

        # create and run the rancher-compose up command
        stack_name = self.get_stack_name(mv)
        cmd_list = [self.RANCHER_COMPOSE_BIN, '-p', stack_name, 'up', '-d']
        try:
            p = subprocess.Popen(cmd_list, stdout=subprocess.PIPE, env=eenv, cwd=ymlpath)
            stdout, stderr = p.communicate()
        except:
            pprint(traceback.format_exc())
            raise ValueError('Unable to start service: Error calling rancher-compose: '+traceback.format_exc())

        print('STDOUT:')
        print(stdout)
        print('STDERR:')
        print(stderr)

        if p.returncode != 0:
            raise ValueError('Unable to start service: Error was: \n' + stdout);

        #END start
        pass

    def stop(self, ctx, service):
        """
        :param service: instance of type "Service" (version - unified version
           field including semantic version, git commit hash and case of last
           version of tag (dev/beta/release).) -> structure: parameter
           "module_name" of String, parameter "version" of String
        """
        # ctx is the context object
        #BEGIN stop
        print('STOPPING: ' + str(service))

        # lookup the module info from the catalog
        cc = Catalog(CATALOG_URL, token=ctx['token'])
        mv = cc.get_module_version({'module_name' : service['module_name'], 'version' : service['version']})
        

        docker_compose, rancher_compose = self.create_compose_files(mv)

        with open('docker-compose.yml', 'w') as outfile:
            outfile.write( yaml.safe_dump(docker_compose, default_flow_style=False) )
        with open('rancher-compose.yml', 'w') as outfile:
            outfile.write( yaml.safe_dump(rancher_compose, default_flow_style=False) )

        eenv = os.environ.copy()
        eenv['RANCHER_URL'] = self.deploy_config['rancher-env-url']
        eenv['RANCHER_ACCESS_KEY'] = self.deploy_config['access-key']
        eenv['RANCHER_SECRET_KEY'] = self.deploy_config['secret-key']
        cmd_list = ['rancher-compose', '-p', catalog_module_name, 'stop']
        try:
            tool_process = subprocess.Popen(cmd_list, stderr=subprocess.PIPE, env=eenv)
            stdout, stderr = tool_process.communicate()
            pprint(stdout)
            pprint(stderr)
        except:
            pprint(traceback.format_exc())
        #END stop
        pass

    def pause(self, ctx, service):
        """
        :param service: instance of type "Service" (version - unified version
           field including semantic version, git commit hash and case of last
           version of tag (dev/beta/release).) -> structure: parameter
           "module_name" of String, parameter "version" of String
        """
        # ctx is the context object
        #BEGIN pause
        #END pause
        pass

    def list_service_status(self, ctx, params):
        """
        :param params: instance of type "ListServiceStatusParams" ->
           structure: parameter "is_up" of type "boolean", parameter
           "module_names" of list of String
        :returns: instance of list of type "ServiceStatus" (version is the
           semantic version of the module) -> structure: parameter
           "module_name" of String, parameter "version" of String, parameter
           "hash" of String, parameter "url" of String, parameter "node" of
           String, parameter "up" of type "boolean", parameter "status" of
           String, parameter "health" of String, parameter
           "last_request_timestamp" of String
        """
        # ctx is the context object
        # return variables are: returnVal
        #BEGIN list_service_status
        client = gdapi.Client(url=self.deploy_config['rancher-env-url'],
                      access_key=self.deploy_config['access-key'],
                      secret_key=self.deploy_config['secret-key'])

        cc = Catalog(CATALOG_URL, token=ctx['token'])

        # get environment id
        result = []
        slists = client.list_environment()
        if len(slists) == 0: return [] # I shouldn't return 
        for slist in slists:
          eid = slist['id']
  
          # get service info
          entries = client.list_service(environmentId = eid)
          if len(entries) == 0: continue
         
          for entry in entries:
            rs = entry['name'].split('-')
            if len(rs) != 2: continue
            es = {'module_name' : rs[0], 'status' : entry['state'], 'health' : entry['healthState'], 'hash' : rs[1]}
            #if es['health'] == 'healthy' and es['status'] == 'active':
            if es['status'] == 'active':
              es['up'] = 1
            else:
              es['up'] = 0
            try:
              mv = cc.module_version_lookup({'module_name' : rs[0], 'lookup' : rs[1]})
              es['url'] = "https://{0}:{1}/dynserv/{3}.{2}".format(self.deploy_config['svc-hostname'], self.deploy_config['nginx-port'], mv['module_name'], mv['git_commit_hash'])
              es['version'] = mv['version']
            except:
              # this may occur if the module version is not registered with the catalog, or is not a service
              es['url'] = "https://{0}:{1}/dynserv/{3}.{2}".format(self.deploy_config['svc-hostname'], self.deploy_config['nginx-port'], rs[0], rs[1])
              es['version'] = 'unknown'
            result.append(es)

        returnVal = result
        #END list_service_status

        # At some point might do deeper type checking...
        if not isinstance(returnVal, list):
            raise ValueError('Method list_service_status return value ' +
                             'returnVal is not type list as required.')
        # return the results
        return [returnVal]

    def get_service_status(self, ctx, service):
        """
        :param service: instance of type "Service" (version - unified version
           field including semantic version, git commit hash and case of last
           version of tag (dev/beta/release).) -> structure: parameter
           "module_name" of String, parameter "version" of String
        :returns: instance of type "ServiceStatus" (version is the semantic
           version of the module) -> structure: parameter "module_name" of
           String, parameter "version" of String, parameter "hash" of String,
           parameter "url" of String, parameter "node" of String, parameter
           "up" of type "boolean", parameter "status" of String, parameter
           "health" of String, parameter "last_request_timestamp" of String
        """
        # ctx is the context object
        # return variables are: returnVal
        #BEGIN get_service_status
        # TODO: handle case where version is not registered in the catalog- this may be the case for core services
        #       that were not registered in the usual way.
        cc = Catalog(self.deploy_config['catalog-url'], token=ctx['token'])
        mv = cc.get_module_version({'module_name' : service['module_name'], 'version' : service['version']})
        shash = mv['git_commit_hash']
        client = gdapi.Client(url=self.deploy_config['rancher-env-url'],
                      access_key=self.deploy_config['access-key'],
                      secret_key=self.deploy_config['secret-key'])
        
        returnVal = None

        # get environment id
        slist = client.list_environment(name=service['module_name'])
        if len(slist) == 0: return None
        eid = slist[0]['id']

        # get service info
        entry = client.list_service(environmentId = eid, name = '{0}-{1}'.format(service['module_name'],shash))
        if len(entry) == 0: return None
        entry = entry[0]
        returnVal = {'module_name' : service['module_name'], 'status' : entry['state'], 'health' : entry['healthState']}
        returnVal['hash'] = shash
        #if es['health'] == 'healthy' and es['status'] == 'active':
        if returnVal['status'] == 'active':
          returnVal['up'] = 1
        else:
          returnVal['up'] = 0
        returnVal['url'] = "https://{0}:{1}/dynserv/{3}.{2}".format(self.deploy_config['svc-hostname'], self.deploy_config['nginx-port'], mv['module_name'], shash)
        returnVal['version'] = mv['version']
        #END get_service_status

        # At some point might do deeper type checking...
        if not isinstance(returnVal, dict):
            raise ValueError('Method get_service_status return value ' +
                             'returnVal is not type dict as required.')
        # return the results
        return [returnVal]

    def status(self, ctx):
        #BEGIN_STATUS
        returnVal = {'state': "OK", 'message': "", 'version': self.VERSION, 
                     'git_url': self.GIT_URL, 'git_commit_hash': self.GIT_COMMIT_HASH}
        #END_STATUS
        return [returnVal]
