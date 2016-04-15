#BEGIN_HEADER
import os
import time
import yaml
import subprocess
from  pprint import pprint
import traceback
import gdapi
import json
import zipfile
from StringIO import StringIO
import re
from urlparse import urlparse
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
    GIT_URL = "https://github.com/msneddon/service_wizard"
    GIT_COMMIT_HASH = "84d4cbff7a256f9c6f28bdb7f1dcad57312b58e3"
    
    #BEGIN_CLASS_HEADER
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
        #END_CONSTRUCTOR
        pass
    

    def start(self, ctx, service):
        # ctx is the context object
        #BEGIN start
        cc = Catalog(self.deploy_config['catalog-url'], token=ctx['token'])
        #TODO: not working yet
        #mv = cc.module_version_lookup({'module_name' : service['module_name']})
        mv = cc.module_version_lookup({'module_name' : service['module_name'], 'lookup' : service['version']})
        shash = mv['git_commit_hash']
        # Use the name returned from the catalog service
        catalog_module_name = mv['module_name']
        #shash = service['version']
        sname = "{0}-{1}".format(catalog_module_name,shash) # service name
        docker_compose = { shash : {
                   "image" : "rancher/dns-service",
                   "links" : ["{0}:{0}".format(sname)]
                 },
                 sname : {
                   "image" : mv['docker_img_name']
                 }
               }

        ymlpath = self.deploy_config['temp-dir'] + '/' + service['module_name'] + '/' + str(int(time.time()))
        os.makedirs(ymlpath)

        docker_compose_path=ymlpath + '/docker-compose.yml'
        rancher_compose_path=ymlpath + '/rancher-compose.yml'

        with open(docker_compose_path, 'w') as outfile:
            outfile.write( yaml.safe_dump(docker_compose, default_flow_style=False) )
        # can be extended later
        with open(rancher_compose_path, 'w') as outfile:
            outfile.write( yaml.safe_dump({sname:{'scale':1}}, default_flow_style=False) )
        eenv = os.environ.copy()
        eenv['RANCHER_URL'] = self.deploy_config['rancher-env-url']
        eenv['RANCHER_ACCESS_KEY'] = self.deploy_config['access-key']
        eenv['RANCHER_SECRET_KEY'] = self.deploy_config['secret-key']
        cmd_list = ['rancher-compose', '-p', service['module_name'], 'up', '-d']
        try:
            tool_process = subprocess.Popen(cmd_list, stderr=subprocess.PIPE, env=eenv)
            stdout, stderr = tool_process.communicate()
            pprint(stdout)
            pprint(stderr)
        except:
            pprint(traceback.format_exc())
        #END start
        pass

    def stop(self, ctx, service):
        # ctx is the context object
        #BEGIN stop
        cc = Catalog(self.deploy_config['catalog-url'], token=ctx['token'])
        mv = cc.module_version_lookup({'module_name' : service['module_name'], 'lookup' : service['version']})
        shash = mv['git_commit_hash']
        sname = "{0}-{1}".format(service['module_name'],shash) # service name
        docker_compose = { shash : {
                   "image" : "rancher/dns-service",
                   "links" : ["{0}:{0}".format(sname)]
                 },
                 sname : {
                   "image" : "{0}/kbase:{1}.{2}".format(self.deploy_config['docker-registry-url'],service['module_name'],shash)
                 }
               }
        with open('docker-compose.yml', 'w') as outfile:
            outfile.write( yaml.safe_dump(docker_compose, default_flow_style=False) )
        # can be extended later
        with open('rancher-compose.yml', 'w') as outfile:
            outfile.write( yaml.safe_dump({sname:{'scale':1}}, default_flow_style=False) )
        eenv = os.environ.copy()
        eenv['RANCHER_URL'] = self.deploy_config['rancher-env-url']
        eenv['RANCHER_ACCESS_KEY'] = self.deploy_config['access-key']
        eenv['RANCHER_SECRET_KEY'] = self.deploy_config['secret-key']
        cmd_list = ['rancher-compose', '-p', service['module_name'], 'stop']
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
        # ctx is the context object
        #BEGIN pause
        #END pause
        pass

    def list_service_status(self, ctx, params):
        # ctx is the context object
        # return variables are: returnVal
        #BEGIN list_service_status
        client = gdapi.Client(url=self.deploy_config['rancher-env-url'],
                      access_key=self.deploy_config['access-key'],
                      secret_key=self.deploy_config['secret-key'])
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
            es['url'] = "https://{0}:{1}/dynserv/{2}-{3}.{2}".format(self.deploy_config['svc-hostname'], self.deploy_config['nginx-port'], rs[0], rs[1])
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
        # ctx is the context object
        # return variables are: returnVal
        #BEGIN get_service_status
        cc = Catalog(self.deploy_config['catalog-url'], token=ctx['token'])
        mv = cc.module_version_lookup({'module_name' : service['module_name'], 'lookup' : service['version']})
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
        returnVal['url'] = "https://{0}:{1}/dynserv/{2}-{3}.{2}".format(self.deploy_config['svc-hostname'], self.deploy_config['nginx-port'], service['module_name'], shash)
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
