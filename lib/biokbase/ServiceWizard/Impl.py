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

        rancher = gdapi.Client(url=self.deploy_config['rancher-env-url'],
                      access_key=self.deploy_config['access-key'],
                      secret_key=self.deploy_config['secret-key'])

        stacks = rancher.list_environment(name=service_name)

        # there should be only one stack, but what if there is more than one?
        if (len(stacks) > 0):
            exportConfigURL=stacks[0]['actions']['exportconfig']

            payload = {'serviceIds':[]}
            configReq = requests.post(exportConfigURL, data = json.dumps(payload), auth=(self.deploy_config['access-key'],self.deploy_config['secret-key']),verify=False)
            export=configReq.json()
            docker_compose = yaml.load(export['dockerComposeConfig'])
            rancher_compose = yaml.load(export['rancherComposeConfig'])
        else:
            docker_compose = {}
            rancher_compose = {}

        docker_compose[dns_service_name] = {
                "image" : "rancher/dns-service",
                "links" : [ service_name+':'+service_name ]
            }
        docker_compose[service_name] = {
                "image" : module_version['docker_img_name']
            }

        rancher_compose[service_name] = {
                "scale" : 1
            }

        return docker_compose, rancher_compose

    def get_service_url(self, module_version):
        url = "https://{0}:{1}/dynserv/{3}.{2}"
        url = url.format(
                    self.SVC_HOSTNAME, 
                    self.NGINX_PORT, 
                    self.get_stack_name(module_version),
                    self.get_dns_service_name(module_version))
        return url


    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        self.VERSION = '0.2.0'
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

        if 'svc-hostname' not in config:
            raise ValueError('"svc-hostname" configuration variable not set"')
        self.SVC_HOSTNAME = config['svc-hostname']

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
        :param service: instance of type "Service" (version - unified version
           field including semantic version, git commit hash and case of last
           version of tag (dev/beta/release).) -> structure: parameter
           "module_name" of String, parameter "version" of String
        """
        # ctx is the context object
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
        print('STOP REQUEST: ' + str(service))

        # lookup the module info from the catalog
        cc = Catalog(self.CATALOG_URL, token=ctx['token'])
        mv = cc.get_module_version({'module_name' : service['module_name'], 'version' : service['version']})
        
        docker_compose, rancher_compose = self.create_compose_files(mv)

        ymlpath = self.SCRATCH_DIR + '/' + mv['module_name'] + '/' + str(int(time.time()))
        os.makedirs(ymlpath)
        docker_compose_path=ymlpath + '/docker-compose.yml'
        rancher_compose_path=ymlpath + '/rancher-compose.yml'

        with open(docker_compose_path, 'w') as outfile:
            outfile.write( yaml.safe_dump(docker_compose, default_flow_style=False) )
        with open(rancher_compose_path, 'w') as outfile:
            outfile.write( yaml.safe_dump(rancher_compose, default_flow_style=False) )

        eenv = os.environ.copy()
        eenv['RANCHER_URL'] = self.deploy_config['rancher-env-url']
        eenv['RANCHER_ACCESS_KEY'] = self.deploy_config['access-key']
        eenv['RANCHER_SECRET_KEY'] = self.deploy_config['secret-key']

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
        rancher = gdapi.Client(url=self.deploy_config['rancher-env-url'],
                      access_key=self.deploy_config['access-key'],
                      secret_key=self.deploy_config['secret-key'])

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
              es['module_name'] = mv['module_name'], 
            except:
              # this will occur if the module version is not registered with the catalog, or if the module
              # was not marked as a service, or if something was started in Rancher directly and pulled
              # from somewhere else, or an old version of the catalog was used to start this service
              es['url'] = "https://{0}:{1}/dynserv/{3}.{2}".format(self.deploy_config['svc-hostname'], self.deploy_config['nginx-port'], rs[0], rs[1])
              es['version'] = ''
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
        cc = Catalog(self.CATALOG_URL, token=ctx['token'])
        mv = cc.get_module_version({'module_name' : service['module_name'], 'version' : service['version']})

        stack_name = self.get_stack_name(mv)

        rancher = gdapi.Client(url=self.deploy_config['rancher-env-url'],
                      access_key=self.deploy_config['access-key'],
                      secret_key=self.deploy_config['secret-key'])
        
        returnVal = None

        # get environment id
        slist = rancher.list_environment(name=stack_name)
        if len(slist) == 0: 
            return None
        eid = slist[0]['id']

        # get service info
        entry = rancher.list_service(environmentId=eid, name=self.get_service_name(mv))
        if len(entry) == 0: return None
        entry = entry[0]

        returnVal = {'module_name' : service['module_name'], 'status' : entry['state'], 'health' : entry['healthState']}

        returnVal['hash'] = mv['git_commit_hash']
        if returnVal['status'] == 'active':
          returnVal['up'] = 1
        else:
          returnVal['up'] = 0
        returnVal['url'] = self.get_service_url(mv)
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
