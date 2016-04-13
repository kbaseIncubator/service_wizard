#BEGIN_HEADER
import os
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
        if 'ngix-port' not in config:
            self.deploy_config['ngix-port'] = 7443
        
        #END_CONSTRUCTOR
        pass

    def start(self, ctx, service):
        # ctx is the context object
        #BEGIN start
        shash = service['version'] #TODO: need to convert service version to hash
        docker_compose = { shash : {
                   "image" : "rancher/dns-service",
                   "links" : ["{0}:{1}".format(service['module_name'],service['module_name'])]
                 },
                 service['module_name'] : {
                   "image" : "dockerhub-ci.kbase.us/kbase:{0}.{1}".format(service['module_name'],shash)
                 }
               }
        with open('docker-compose.yml', 'w') as outfile:
            outfile.write( yaml.safe_dump(docker_compose, default_flow_style=False) )
        # can be extended later
        with open('rancher-compose.yml', 'w') as outfile:
            outfile.write( yaml.safe_dump({service['module_name']:{'scale':1}}, default_flow_style=False) )
        eenv = os.environ.copy()
        eenv['RANCHER_URL'] = self.deploy_config['rancher-env-url']
        eenv['RANCHER_ACCESS_KEY'] = self.deploy_config['access-key']
        eenv['RANCHER_SECRET_KEY'] = self.deploy_config['secret-key']
        cmd_list = ['./bin/rancher-compose', '-p', service['module_name'], 'up', '-d']
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
        shash = service['version'] #TODO: need to convert service version to hash
        docker_compose = { shash : {
                   "image" : "rancher/dns-service",
                   "links" : ["{0}:{1}".format(service['module_name'],service['module_name'])]
                 },
                 service['module_name'] : {
                   "image" : "dockerhub-ci.kbase.us/kbase:{0}.{1}".format(service['module_name'],shash)
                 }
               }
        with open('docker-compose.yml', 'w') as outfile:
            outfile.write( yaml.safe_dump(docker_compose, default_flow_style=False) )
        # can be extended later
        with open('rancher-compose.yml', 'w') as outfile:
            outfile.write( yaml.safe_dump({service['module_name']:{'scale':1}}, default_flow_style=False) )
        eenv = os.environ.copy()
        eenv['RANCHER_URL'] = self.deploy_config['rancher-env-url']
        eenv['RANCHER_ACCESS_KEY'] = self.deploy_config['access-key']
        eenv['RANCHER_SECRET_KEY'] = self.deploy_config['secret-key']
        cmd_list = ['./bin/rancher-compose', '-p', service['module_name'], 'stop']
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
        slist = client.list('environment')

        result = []
        for entry in slist:
          if entry['type'] == 'environment':
            es = {'module_name' : entry['name'], 'status' : entry['state'], 'health' : entry['healthState']}
            # the following will be changed later but only for now
            sr = client._session.get("{0}/environments/{1}/composeconfig".format(self.deploy_config['rancher-env-url'], entry['id']), auth=client._auth, params=None, headers=client._headers)
            if sr.ok: 
              dc=yaml.load(zipfile.ZipFile(StringIO(sr.content), "r").read('docker-compose.yml'))
              if entry['name'] in dc and 'image' in dc[entry['name']] and re.match(r'^dockerhub-', dc[entry['name']]['image']):
                for hk in dc.keys():
                  if hk != entry['name']:
                    es['hash'] = hk
                    #if es['health'] == 'healthy' and es['status'] == 'active':
                    if es['status'] == 'active':
                      es['up'] = 1
                    else:
                      es['up'] = 0
                    es['url'] = "https://{0}:{1}/dynserv/{2}-{3}.{2}".format(self.deploy_config['svc-hostname'], self.deploy_config['ngix-port'], entry['name'], es['hash'])
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
        shash = service['version'] #TODO: need to convert service version to hash
        client = gdapi.Client(url=self.deploy_config['rancher-env-url'],
                      access_key=self.deploy_config['access-key'],
                      secret_key=self.deploy_config['secret-key'])
        slist = client.list('environment')

        returnVal = None
        for entry in slist:
          if entry['type'] == 'environment':
            if entry['name'] != service['name']:
              continue
            es = {'module_name' : entry['name'], 'status' : entry['state'], 'health' : entry['healthState']}
            # the following will be changed later but only for now
            sr = client._session.get("{0}/environments/{1}/composeconfig".format(self.deploy_config['rancher-env-url'], entry['id']), auth=client._auth, params=None, headers=client._headers)
            if sr.ok: 
              dc=yaml.load(zipfile.ZipFile(StringIO(sr.content), "r").read('docker-compose.yml'))
              if entry['name'] in dc and 'image' in dc[entry['name']] and re.match(r'^dockerhub-', dc[entry['name']]['image']):
                for hk in dc.keys():
                  if hk != entry['name']:
                    if hk != shash: continue
                    es['hash'] = hk
                    #if es['health'] == 'healthy' and es['status'] == 'active':
                    if es['status'] == 'active':
                      es['up'] = 1
                    else:
                      es['up'] = 0
                    es['url'] = "https://{0}:{1}/dynserv/{2}-{3}.{2}".format(self.deploy_config['svc-hostname'], self.deploy_config['ngix-port'], entry['name'], es['hash'])
                    returnVal = es
        #END get_service_status

        # At some point might do deeper type checking...
        if not isinstance(returnVal, dict):
            raise ValueError('Method get_service_status return value ' +
                             'returnVal is not type dict as required.')
        # return the results
        return [returnVal]
