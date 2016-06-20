#BEGIN_HEADER
import os
import time
import yaml
import subprocess
from pprint import pprint, pformat
import traceback
import gdapi
import json
import zipfile
from StringIO import StringIO
import re
from urlparse import urlparse

from websocket import create_connection

import base64
import hashlib

import requests

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
    VERSION = "0.3.0"
    GIT_URL = "git@github.com:msneddon/service_wizard.git"
    GIT_COMMIT_HASH = "7ce70ba16d70429ee6fea6cddd914abea4fb4dec"
    
    #BEGIN_CLASS_HEADER

    RANCHER_COMPOSE_BIN = 'rancher-compose'
    RANCHER_URL = ''
    USE_RANCHER_ACCESS_KEY = True
    RANCHER_ACCESS_KEY = ''
    RANCHER_SECRET_KEY = ''

    CATALOG_URL = ''
    SCRATCH_DIR = ''

    SVC_HOSTNAME = ''
    NGINX_PORT = ''

    # Given module information, generate a unique stack name for that version
    def get_stack_name(self, module_version):
        name = module_version['module_name'] #+ '-'+module_version['version'] + '-' + module_version['git_commit_hash'][:7]
        # stack names must have dashes, not underscores
        name = name.replace('_','-')
        # stack names must have dashes, not dots
        name = name.replace('.','-')
        return name

    def get_module_name_hash(self, module_name):
        return hashlib.md5(module_name).hexdigest()[:20]

    def get_service_name(self, module_version):
        # hash the module name so we don't have to deal with illegal characters, length limits, etc
        module_name_hash = self.get_module_name_hash(module_version['module_name'])
        git_commit_hash = module_version['git_commit_hash']
        return module_name_hash + '-' + git_commit_hash

    def get_dns_service_name(self, module_version):
        dns_service_name = module_version['git_commit_hash']
        return dns_service_name

    # Build the docker_compose and rancher_compose files
    def create_compose_files(self, module_version):
        # in progress: pull the existing config from rancher and include in new config
        # 1) look up service name to get project/environment
        # 2) POST  {"serviceIds":[]} to /v1/projects/$projid/environments/$envid/?action=exportconfig
        # parse dockerComposeConfig and rancherComposeConfig as yml

        # construct the service names
        service_name = self.get_service_name(module_version)
        dns_service_name = self.get_dns_service_name(module_version)

        rancher = gdapi.Client(url=self.RANCHER_URL,
                      access_key=self.RANCHER_ACCESS_KEY,
                      secret_key=self.RANCHER_SECRET_KEY)

        stacks = rancher.list_environment(name=self.get_stack_name(module_version))

        # there should be only one stack, but what if there is more than one?
        is_new_stack = False
        if (stacks is None or len(stacks) == 0):
            is_new_stack = True

        # code to fetch existing docker_compose and rancher_compose files
        #if len(stacks) > 0:
        #    exportConfigURL=stacks[0]['actions']['exportconfig']
        #    payload = {'serviceIds':[]}
        #    configReq = requests.post(exportConfigURL, data = json.dumps(payload), auth=(self.RANCHER_ACCESS_KEY,self.RANCHER_SECRET_KEY),verify=False)
        #    export=configReq.json()
        #    docker_compose = yaml.load(export['dockerComposeConfig'])
        #    rancher_compose = yaml.load(export['rancherComposeConfig'])

        docker_compose = {}
        rancher_compose = {}

        docker_compose[dns_service_name] = {
                "image" : "rancher/dns-service",
                "links" : [ service_name+':'+service_name ]
            }
        docker_compose[service_name] = {
                "image" : module_version['docker_img_name'],
                "labels" : {
                    'us.kbase.module.version':module_version['version'],
                    'us.kbase.module.git_commit_hash':module_version['git_commit_hash']
                },
                "environment" : {
                    'KBASE_ENDPOINT' : self.KBASE_ENDPOINT
                }
            }

        rancher_compose[service_name] = {
                "scale" : 1
            }

        return docker_compose, rancher_compose, is_new_stack

    def set_stack_description(self, module_version):
        pprint('setting stack description')
        rancher = gdapi.Client(url=self.RANCHER_URL,access_key=self.RANCHER_ACCESS_KEY,secret_key=self.RANCHER_SECRET_KEY)
        stacks = rancher.list_environment(name=self.get_stack_name(module_version))
        pprint(len(stacks))
        pprint(module_version)
        if (len(stacks) > 0):
            exportConfigURL=stacks[0]['actions']['update']
            payload = {'description': module_version['git_url'] }
            x = requests.put(exportConfigURL, data = json.dumps(payload), auth=(self.RANCHER_ACCESS_KEY,self.RANCHER_SECRET_KEY),verify=False)


    def get_service_url(self, module_version):
        url = "https://{0}:{1}/dynserv/{3}.{2}"
        url = url.format(
                    self.SVC_HOSTNAME, 
                    self.NGINX_PORT, 
                    self.get_stack_name(module_version),
                    self.get_dns_service_name(module_version))
        return url


    def get_single_service_status(self, module_version):

        stack_name = self.get_stack_name(module_version)
        rancher = gdapi.Client(url=self.RANCHER_URL,access_key=self.RANCHER_ACCESS_KEY,secret_key=self.RANCHER_SECRET_KEY)
        
        # lookup environment id (this may become a deployment config option)
        slist = rancher.list_environment(name=stack_name)
        if len(slist) == 0: 
            return None
        eid = slist[0]['id']

        # get service info
        entry = rancher.list_service(environmentId=eid, name=self.get_service_name(module_version))
        if len(entry) == 0: 
            return None
        entry = entry[0]

        status = {
            'module_name':module_version['module_name'],
            'release_tags':module_version['release_tags'],
            'git_commit_hash':module_version['git_commit_hash'],
            'hash':module_version['git_commit_hash'],
            'version':module_version['version'],
            'url': self.get_service_url(module_version),
            'status' : entry['state'],
            'health' : entry['healthState'],
            'up' : 1 if entry['state']=='active' else 0
        }
        return status


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

        if 'rancher-env-url' not in config:
            raise ValueError('"rancher-env-url" configuration variable not set"')
        self.RANCHER_URL = config['rancher-env-url']

        if 'temp-dir' not in config:
            raise ValueError('"temp-dir" configuration variable not set"')
        self.SCRATCH_DIR = config['temp-dir']

        if 'svc-hostname' not in config:
            raise ValueError('"svc-hostname" configuration variable not set"')
        self.SVC_HOSTNAME = config['svc-hostname']

        if 'kbase-endpoint' not in config:
            raise ValueError('"kbase-endpoint" configuration variable not set"')
        self.KBASE_ENDPOINT = config['kbase-endpoint']

        if 'nginx-port' not in config:
            raise ValueError('"nginx-port" configuration variable not set"')
        self.NGINX_PORT = config['nginx-port']

        if not os.path.isfile(self.RANCHER_COMPOSE_BIN):
            print('WARNING: rancher-compose (='+self.RANCHER_COMPOSE_BIN+') command not found.  Set absolute location with "rancher-compose-bin" configuration.')

        if ('access-key' not in config) or ('secret-key' not in config):
            self.USE_RANCHER_ACCESS_KEY = False
            print('WARNING: No "access-key" and "secret-key" set for Rancher.  Will connect unauthenticated, which should only be used in test environments.')
        else:
            self.RANCHER_ACCESS_KEY = config['access-key']
            self.RANCHER_SECRET_KEY = config['secret-key']

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
        version=self.VERSION
        #END version

        # At some point might do deeper type checking...
        if not isinstance(version, basestring):
            raise ValueError('Method version return value ' +
                             'version is not type basestring as required.')
        # return the results
        return [version]

    def start(self, ctx, service):
        """
        Try to start the specified service; this will generate an error if the
        specified service cannot be started.  If the startup did not give any
        errors, then the status of the running service is provided.
        :param service: instance of type "Service" (module_name - the name of
           the service module, case-insensitive version     - specify the
           service version, which can be either: (1) full git commit hash of
           the module version (2) semantic version or semantic version
           specification Note: semantic version lookup will only work for
           released versions of the module. (3) release tag, which is one of:
           dev | beta | release This information is always fetched from the
           Catalog, so for more details on specifying the version, see the
           Catalog documentation for the get_module_version method.) ->
           structure: parameter "module_name" of String, parameter "version"
           of String
        :returns: instance of type "ServiceStatus" (module_name     - name of
           the service module version         - semantic version number of
           the service module git_commit_hash - git commit hash of the
           service module release_tags    - list of release tags currently
           for this service module (dev/beta/release) url             - the
           url of the service up              - 1 if the service is up, 0
           otherwise status          - status of the service as reported by
           rancher health          - health of the service as reported by
           Rancher TODO: add something to return: string
           last_request_timestamp;) -> structure: parameter "module_name" of
           String, parameter "version" of String, parameter "git_commit_hash"
           of String, parameter "release_tags" of list of String, parameter
           "hash" of String, parameter "url" of String, parameter "up" of
           type "boolean", parameter "status" of String, parameter "health"
           of String
        """
        # ctx is the context object
        # return variables are: status
        #BEGIN start

        print('START REQUEST: ' + str(service))

        # First, lookup the module information from the catalog, make sure it is a service
        cc = Catalog(self.CATALOG_URL, token=ctx['token'])
        mv = cc.get_module_version({'module_name' : service['module_name'], 'version' : service['version']})
        if 'dynamic_service' not in mv:
            raise ValueError('Specified module is not marked as a dynamic service. ('+mv['module_name']+'-' + mv['git_commit_hash']+')')
        if mv['dynamic_service'] != 1:
            raise ValueError('Specified module is not marked as a dynamic service. ('+mv['module_name']+'-' + mv['git_commit_hash']+')')

        # Construct the docker compose and rancher compose file
        docker_compose, rancher_compose, is_new_stack = self.create_compose_files(mv)

        # To do: try to use API to send docker-compose directly instead of needing to write to disk
        ymlpath = self.SCRATCH_DIR + '/' + mv['module_name'] + '/' + str(int(time.time()*1000))
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
        eenv['RANCHER_URL'] = self.RANCHER_URL
        if self.USE_RANCHER_ACCESS_KEY:
            eenv['RANCHER_ACCESS_KEY'] = self.RANCHER_ACCESS_KEY
            eenv['RANCHER_SECRET_KEY'] = self.RANCHER_SECRET_KEY

        # create and run the rancher-compose up command
        stack_name = self.get_stack_name(mv)
        print('STARTING STACK: ' + stack_name)
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

        # if it is a new stack, then set a description string
        if is_new_stack:
            self.set_stack_description(mv)

        status = self.get_single_service_status(mv)
        # if there is some delay in starting up, then give it a couple seconds
        for trys in range(0,5):
            if status is None or status['up']!=1:
                time.sleep(2)
                status = self.get_single_service_status(mv)
            else: break

        #END start

        # At some point might do deeper type checking...
        if not isinstance(status, dict):
            raise ValueError('Method start return value ' +
                             'status is not type dict as required.')
        # return the results
        return [status]

    def stop(self, ctx, service):
        """
        Try to stop the specified service; this will generate an error if the
        specified service cannot be stopped.  If the stop did not give any
        errors, then the status of the stopped service is provided.
        :param service: instance of type "Service" (module_name - the name of
           the service module, case-insensitive version     - specify the
           service version, which can be either: (1) full git commit hash of
           the module version (2) semantic version or semantic version
           specification Note: semantic version lookup will only work for
           released versions of the module. (3) release tag, which is one of:
           dev | beta | release This information is always fetched from the
           Catalog, so for more details on specifying the version, see the
           Catalog documentation for the get_module_version method.) ->
           structure: parameter "module_name" of String, parameter "version"
           of String
        :returns: instance of type "ServiceStatus" (module_name     - name of
           the service module version         - semantic version number of
           the service module git_commit_hash - git commit hash of the
           service module release_tags    - list of release tags currently
           for this service module (dev/beta/release) url             - the
           url of the service up              - 1 if the service is up, 0
           otherwise status          - status of the service as reported by
           rancher health          - health of the service as reported by
           Rancher TODO: add something to return: string
           last_request_timestamp;) -> structure: parameter "module_name" of
           String, parameter "version" of String, parameter "git_commit_hash"
           of String, parameter "release_tags" of list of String, parameter
           "hash" of String, parameter "url" of String, parameter "up" of
           type "boolean", parameter "status" of String, parameter "health"
           of String
        """
        # ctx is the context object
        # return variables are: status
        #BEGIN stop
        print('STOP REQUEST: ' + str(service))

        # lookup the module info from the catalog
        cc = Catalog(self.CATALOG_URL, token=ctx['token'])
        mv = cc.get_module_version({'module_name' : service['module_name'], 'version' : service['version']})
        if 'dynamic_service' not in mv:
            raise ValueError('Specified module is not marked as a dynamic service. ('+mv['module_name']+'-' + mv['git_commit_hash']+')')
        if mv['dynamic_service'] != 1:
            raise ValueError('Specified module is not marked as a dynamic service. ('+mv['module_name']+'-' + mv['git_commit_hash']+')')
        
        docker_compose, rancher_compose, is_new_stack = self.create_compose_files(mv)

        ymlpath = self.SCRATCH_DIR + '/' + mv['module_name'] + '/' + str(int(time.time()*1000))
        os.makedirs(ymlpath)
        docker_compose_path=ymlpath + '/docker-compose.yml'
        rancher_compose_path=ymlpath + '/rancher-compose.yml'

        with open(docker_compose_path, 'w') as outfile:
            outfile.write( yaml.safe_dump(docker_compose, default_flow_style=False) )
        with open(rancher_compose_path, 'w') as outfile:
            outfile.write( yaml.safe_dump(rancher_compose, default_flow_style=False) )

        eenv = os.environ.copy()
        eenv['RANCHER_URL'] = self.RANCHER_URL
        eenv['RANCHER_ACCESS_KEY'] = self.RANCHER_ACCESS_KEY
        eenv['RANCHER_SECRET_KEY'] = self.RANCHER_SECRET_KEY

        stack_name = self.get_stack_name(mv)
        print('STOPPING STACK: ' + stack_name)
        cmd_list = [self.RANCHER_COMPOSE_BIN, '-p', stack_name, 'stop']
        try:
            p = subprocess.Popen(cmd_list, stdout=subprocess.PIPE, env=eenv, cwd=ymlpath)
            stdout, stderr = p.communicate()
        except:
            pprint(traceback.format_exc())
            raise ValueError('Unable to stop service: Error calling rancher-compose: '+traceback.format_exc())

        print('STDOUT:')
        print(stdout)
        print('STDERR:')
        print(stderr)

        status = self.get_single_service_status(mv)
        #END stop

        # At some point might do deeper type checking...
        if not isinstance(status, dict):
            raise ValueError('Method stop return value ' +
                             'status is not type dict as required.')
        # return the results
        return [status]

    def list_service_status(self, ctx, params):
        """
        :param params: instance of type "ListServiceStatusParams" (not yet
           implemented funcdef pause(Service service) returns (ServiceStatus
           status);) -> structure: parameter "is_up" of type "boolean",
           parameter "module_names" of list of String
        :returns: instance of list of type "ServiceStatus" (module_name     -
           name of the service module version         - semantic version
           number of the service module git_commit_hash - git commit hash of
           the service module release_tags    - list of release tags
           currently for this service module (dev/beta/release) url          
           - the url of the service up              - 1 if the service is up,
           0 otherwise status          - status of the service as reported by
           rancher health          - health of the service as reported by
           Rancher TODO: add something to return: string
           last_request_timestamp;) -> structure: parameter "module_name" of
           String, parameter "version" of String, parameter "git_commit_hash"
           of String, parameter "release_tags" of list of String, parameter
           "hash" of String, parameter "url" of String, parameter "up" of
           type "boolean", parameter "status" of String, parameter "health"
           of String
        """
        # ctx is the context object
        # return variables are: returnVal
        #BEGIN list_service_status
        rancher = gdapi.Client(url=self.RANCHER_URL,
                      access_key=self.RANCHER_ACCESS_KEY,
                      secret_key=self.RANCHER_SECRET_KEY)

        cc = Catalog(self.CATALOG_URL, token=ctx['token'])

        # first create simple module_name lookup based on hash (TODO: in catalog, allow us to only fetch dynamic service modules)
        modules = cc.list_basic_module_info({'include_released':1, 'include_unreleased':1})
        module_hash_lookup = {} # hash => module_name
        for m in modules:
            if 'dynamic_service' not in m or m['dynamic_service']!=1:
                continue
            module_hash_lookup[self.get_module_name_hash(m['module_name'])] = m['module_name']

        # next get environment id (could be a config parameter in the future rather than looping over everything)
        result = []
        slists = rancher.list_environment()
        if len(slists) == 0: return [] # I shouldn't return 
        for slist in slists:
          eid = slist['id']
  
          # get service info
          entries = rancher.list_service(environmentId = eid)
          if len(entries) == 0: continue
         
          for entry in entries:
            rs = entry['name'].split('-')
            if len(rs) != 2: continue
            es = {'status' : entry['state'], 'health' : entry['healthState'], 'hash' : rs[1]}
            #if es['health'] == 'healthy' and es['status'] == 'active':
            if es['status'] == 'active':
              es['up'] = 1
            else:
              es['up'] = 0
            try:
              mv = cc.get_module_version({'module_name': module_hash_lookup[rs[0]],'version':rs[1]})
              es['url'] = self.get_service_url(mv)
              es['version'] = mv['version']
              es['module_name'] = mv['module_name']
              es['release_tags'] = mv['release_tags']
              es['git_commit_hash'] = mv['git_commit_hash']
            except:
              # this will occur if the module version is not registered with the catalog, or if the module
              # was not marked as a service, or if something was started in Rancher directly and pulled
              # from somewhere else, or an old version of the catalog was used to start this service
              es['url'] = "https://{0}:{1}/dynserv/{3}.{2}".format(self.SVC_HOSTNAME, self.NGINX_PORT, rs[0], rs[1])
              es['version'] = ''
              es['release_tags'] = []
              es['git_commit_hash'] = ''
              es['module_name'] = '!'+rs[0]+''
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
        For a given service, check on the status.  If the service is down or
        not running, this function will attempt to start or restart the
        service once, then return the status.
        This function will throw an error if the specified service cannot be
        found or encountered errors on startup.
        :param service: instance of type "Service" (module_name - the name of
           the service module, case-insensitive version     - specify the
           service version, which can be either: (1) full git commit hash of
           the module version (2) semantic version or semantic version
           specification Note: semantic version lookup will only work for
           released versions of the module. (3) release tag, which is one of:
           dev | beta | release This information is always fetched from the
           Catalog, so for more details on specifying the version, see the
           Catalog documentation for the get_module_version method.) ->
           structure: parameter "module_name" of String, parameter "version"
           of String
        :returns: instance of type "ServiceStatus" (module_name     - name of
           the service module version         - semantic version number of
           the service module git_commit_hash - git commit hash of the
           service module release_tags    - list of release tags currently
           for this service module (dev/beta/release) url             - the
           url of the service up              - 1 if the service is up, 0
           otherwise status          - status of the service as reported by
           rancher health          - health of the service as reported by
           Rancher TODO: add something to return: string
           last_request_timestamp;) -> structure: parameter "module_name" of
           String, parameter "version" of String, parameter "git_commit_hash"
           of String, parameter "release_tags" of list of String, parameter
           "hash" of String, parameter "url" of String, parameter "up" of
           type "boolean", parameter "status" of String, parameter "health"
           of String
        """
        # ctx is the context object
        # return variables are: status
        #BEGIN get_service_status

        # TODO: handle case where version is not registered in the catalog- this may be the case for core services
        #       that were not registered in the usual way.

        # first get infor from the catalog- it must be a dynamic service
        cc = Catalog(self.CATALOG_URL, token=ctx['token'])
        mv = cc.get_module_version({'module_name' : service['module_name'], 'version' : service['version']})
        if 'dynamic_service' not in mv:
            raise ValueError('Specified module is not marked as a dynamic service. ('+mv['module_name']+'-' + mv['git_commit_hash']+')')
        if mv['dynamic_service'] != 1:
            raise ValueError('Specified module is not marked as a dynamic service. ('+mv['module_name']+'-' + mv['git_commit_hash']+')')

        status = self.get_single_service_status(mv)

        # if we cannot get the status, or it is not up, then try to start it
        if status is None or status['up']!=1:
            self.start(ctx, service)
            # try to get status
            status = self.get_single_service_status(mv)

        if status is None:
            raise ValueError('Unable to get service status, or service was unable to start properly');

        #END get_service_status

        # At some point might do deeper type checking...
        if not isinstance(status, dict):
            raise ValueError('Method get_service_status return value ' +
                             'status is not type dict as required.')
        # return the results
        return [status]

    def get_service_status_without_restart(self, ctx, service):
        """
        :param service: instance of type "Service" (module_name - the name of
           the service module, case-insensitive version     - specify the
           service version, which can be either: (1) full git commit hash of
           the module version (2) semantic version or semantic version
           specification Note: semantic version lookup will only work for
           released versions of the module. (3) release tag, which is one of:
           dev | beta | release This information is always fetched from the
           Catalog, so for more details on specifying the version, see the
           Catalog documentation for the get_module_version method.) ->
           structure: parameter "module_name" of String, parameter "version"
           of String
        :returns: instance of type "ServiceStatus" (module_name     - name of
           the service module version         - semantic version number of
           the service module git_commit_hash - git commit hash of the
           service module release_tags    - list of release tags currently
           for this service module (dev/beta/release) url             - the
           url of the service up              - 1 if the service is up, 0
           otherwise status          - status of the service as reported by
           rancher health          - health of the service as reported by
           Rancher TODO: add something to return: string
           last_request_timestamp;) -> structure: parameter "module_name" of
           String, parameter "version" of String, parameter "git_commit_hash"
           of String, parameter "release_tags" of list of String, parameter
           "hash" of String, parameter "url" of String, parameter "up" of
           type "boolean", parameter "status" of String, parameter "health"
           of String
        """
        # ctx is the context object
        # return variables are: status
        #BEGIN get_service_status_without_restart
        cc = Catalog(self.CATALOG_URL, token=ctx['token'])
        mv = cc.get_module_version({'module_name' : service['module_name'], 'version' : service['version']})
        if 'dynamic_service' not in mv:
            raise ValueError('Specified module is not marked as a dynamic service. ('+mv['module_name']+'-' + mv['git_commit_hash']+')')
        if mv['dynamic_service'] != 1:
            raise ValueError('Specified module is not marked as a dynamic service. ('+mv['module_name']+'-' + mv['git_commit_hash']+')')

        status = self.get_single_service_status(mv)
        #END get_service_status_without_restart

        # At some point might do deeper type checking...
        if not isinstance(status, dict):
            raise ValueError('Method get_service_status_without_restart return value ' +
                             'status is not type dict as required.')
        # return the results
        return [status]

    def get_service_log(self, ctx, params):
        """
        :param params: instance of type "GetServiceLogParams" (optional
           instance_id to get logs for a specific instance.  Otherwise logs
           from all instances are returned, TODO: add line number
           constraints.) -> structure: parameter "service" of type "Service"
           (module_name - the name of the service module, case-insensitive
           version     - specify the service version, which can be either:
           (1) full git commit hash of the module version (2) semantic
           version or semantic version specification Note: semantic version
           lookup will only work for released versions of the module. (3)
           release tag, which is one of: dev | beta | release This
           information is always fetched from the Catalog, so for more
           details on specifying the version, see the Catalog documentation
           for the get_module_version method.) -> structure: parameter
           "module_name" of String, parameter "version" of String, parameter
           "instance_id" of String
        :returns: instance of list of type "ServiceLog" -> structure:
           parameter "instance_id" of String, parameter "log" of list of
           String
        """
        # ctx is the context object
        # return variables are: logs
        #BEGIN get_service_log
        service = params['service']
        user_id = ctx['user_id']
        cc = Catalog(self.CATALOG_URL, token=ctx['token'])
        module = cc.get_module_info({'module_name' : service['module_name']})
        has_access = False
        for o in module['owners']:
            if o == user_id:
                has_access = True
        if not has_access:
            if cc.is_admin(user_id)==1:
                has_access = True

        if not has_access:
            raise ValueError('Only module owners and catalog admins can view service logs.')

        mv = cc.get_module_version({'module_name' : service['module_name'], 'version' : service['version']})
        if 'dynamic_service' not in mv:
            raise ValueError('Specified module is not marked as a dynamic service. ('+mv['module_name']+'-' + mv['git_commit_hash']+')')
        if mv['dynamic_service'] != 1:
            raise ValueError('Specified module is not marked as a dynamic service. ('+mv['module_name']+'-' + mv['git_commit_hash']+')')

        rancher = gdapi.Client(url=self.RANCHER_URL,
                      access_key=self.RANCHER_ACCESS_KEY,
                      secret_key=self.RANCHER_SECRET_KEY)

        #service_info = rancher.list_servicess(name=self.get_service_name(mv))

        GET_SERVICE_URL = self.RANCHER_URL + '/v1/services?name=' + self.get_service_name(mv) + '&include=instances'
        service_info = requests.get(GET_SERVICE_URL, auth=(self.RANCHER_ACCESS_KEY,self.RANCHER_SECRET_KEY),verify=False).json()

        if len(service_info['data'])==0:
            raise ValueError('Unable to fetch service information.  That service version may not be available.')

        if len(service_info['data'][0]['instances'])==0:
            raise ValueError('The service version specified has no available container instances.')

        instances = service_info['data'][0]['instances']

        #pprint(instances)

        match_instance_id = False
        if 'instance_id' in params:
            match_instance_id = True

        logs = []
        for i in instances:
            if match_instance_id and params['instance_id']!=i['id']:
                continue;
            LOG_URL = i['actions']['logs']
            payload = { 'follow':False }
            log_ws = requests.post(LOG_URL, data = json.dumps(payload), auth=(self.RANCHER_ACCESS_KEY,self.RANCHER_SECRET_KEY),verify=False).json()
            #pprint(log_ws)
            SOCKET_URL = log_ws['url'] + '?token=' + log_ws['token']
            #print(SOCKET_URL)
            log_socket = create_connection(SOCKET_URL)
            lines = [];
            while True:
                try:
                    result =  log_socket.recv()
                    if result is None: break
                    lines.append(result)
                except:
                    break
            logs.append({'instance_id':i['id'], 'log':lines })

        #END get_service_log

        # At some point might do deeper type checking...
        if not isinstance(logs, list):
            raise ValueError('Method get_service_log return value ' +
                             'logs is not type list as required.')
        # return the results
        return [logs]

    def get_service_log_web_socket(self, ctx, params):
        """
        returns connection info for a websocket connection to get realtime service logs
        :param params: instance of type "GetServiceLogParams" (optional
           instance_id to get logs for a specific instance.  Otherwise logs
           from all instances are returned, TODO: add line number
           constraints.) -> structure: parameter "service" of type "Service"
           (module_name - the name of the service module, case-insensitive
           version     - specify the service version, which can be either:
           (1) full git commit hash of the module version (2) semantic
           version or semantic version specification Note: semantic version
           lookup will only work for released versions of the module. (3)
           release tag, which is one of: dev | beta | release This
           information is always fetched from the Catalog, so for more
           details on specifying the version, see the Catalog documentation
           for the get_module_version method.) -> structure: parameter
           "module_name" of String, parameter "version" of String, parameter
           "instance_id" of String
        :returns: instance of list of type "ServiceLogWebSocket" ->
           structure: parameter "instance_id" of String, parameter
           "socket_url" of String
        """
        # ctx is the context object
        # return variables are: sockets
        #BEGIN get_service_log_web_socket
        service = params['service']
        user_id = ctx['user_id']
        cc = Catalog(self.CATALOG_URL, token=ctx['token'])
        module = cc.get_module_info({'module_name' : service['module_name']})
        has_access = False
        for o in module['owners']:
            if o == user_id:
                has_access = True
        if not has_access:
            if cc.is_admin(user_id)==1:
                has_access = True

        if not has_access:
            raise ValueError('Only module owners and catalog admins can view service logs.')

        mv = cc.get_module_version({'module_name' : service['module_name'], 'version' : service['version']})
        if 'dynamic_service' not in mv:
            raise ValueError('Specified module is not marked as a dynamic service. ('+mv['module_name']+'-' + mv['git_commit_hash']+')')
        if mv['dynamic_service'] != 1:
            raise ValueError('Specified module is not marked as a dynamic service. ('+mv['module_name']+'-' + mv['git_commit_hash']+')')

        rancher = gdapi.Client(url=self.RANCHER_URL,
                      access_key=self.RANCHER_ACCESS_KEY,
                      secret_key=self.RANCHER_SECRET_KEY)

        #service_info = rancher.list_servicess(name=self.get_service_name(mv))

        GET_SERVICE_URL = self.RANCHER_URL + '/v1/services?name=' + self.get_service_name(mv) + '&include=instances'
        service_info = requests.get(GET_SERVICE_URL, auth=(self.RANCHER_ACCESS_KEY,self.RANCHER_SECRET_KEY),verify=False).json()

        if len(service_info['data'])==0:
            raise ValueError('Unable to fetch service information.  That service version may not be available.')

        if len(service_info['data'][0]['instances'])==0:
            raise ValueError('The service version specified has no available container instances.')

        instances = service_info['data'][0]['instances']

        #pprint(instances)

        match_instance_id = False
        if 'instance_id' in params:
            match_instance_id = True

        sockets = []
        for i in instances:
            if match_instance_id and params['instance_id']!=i['id']:
                continue;
            LOG_URL = i['actions']['logs']
            payload = { 'follow':True }
            log_ws = requests.post(LOG_URL, data = json.dumps(payload), auth=(self.RANCHER_ACCESS_KEY,self.RANCHER_SECRET_KEY),verify=False).json()
            sockets.append({
                    'instance_id':i['id'],
                    'socket_url':log_ws['url'] + '?token=' + log_ws['token']
                })
        
        #END get_service_log_web_socket

        # At some point might do deeper type checking...
        if not isinstance(sockets, list):
            raise ValueError('Method get_service_log_web_socket return value ' +
                             'sockets is not type list as required.')
        # return the results
        return [sockets]

    def status(self, ctx):
        #BEGIN_STATUS
        returnVal = {'state': "OK", 'message': "", 'version': self.VERSION, 
                     'git_url': self.GIT_URL, 'git_commit_hash': self.GIT_COMMIT_HASH}
        #END_STATUS
        return [returnVal]
