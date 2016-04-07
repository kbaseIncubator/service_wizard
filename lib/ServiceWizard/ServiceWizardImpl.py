#BEGIN_HEADER
import os
import yaml
import subprocess
from  pprint import pprint
import traceback
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
        #END_CONSTRUCTOR
        pass

    def start(self, ctx, service):
        # ctx is the context object
        #BEGIN start
        docker_compose = { service['hash'] : {
                   "image" : "rancher/dns-service",
                   "links" : ["{0}:{1}".format(service['module_name'],service['module_name'])]
                 },
                 service['module_name'] : {
                   "image" : "dockerhub-ci.kbase.us/kbase:{0}.{1}".format(service['module_name'],service['hash'])
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
        eenv['RANCHER_SECRET_KEY'] = self.deploy_config['secrete-key']
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
        docker_compose = { service['hash'] : {
                   "image" : "rancher/dns-service",
                   "links" : ["{0}:{1}".format(service['module_name'],service['module_name'])]
                 },
                 service['module_name'] : {
                   "image" : "dockerhub-ci.kbase.us/kbase:{0}.{1}".format(service['module_name'],service['hash'])
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
        eenv['RANCHER_SECRET_KEY'] = self.deploy_config['secrete-key']
        cmd_list = ['./bin/rancher-compose', '-p', service['module_name'], 'stop', '-d']
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
        #END get_service_status

        # At some point might do deeper type checking...
        if not isinstance(returnVal, dict):
            raise ValueError('Method get_service_status return value ' +
                             'returnVal is not type dict as required.')
        # return the results
        return [returnVal]
