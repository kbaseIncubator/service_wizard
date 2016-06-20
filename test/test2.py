
from pprint import pprint
import os, sys
import timeit
testdir = os.path.dirname(os.path.abspath(__file__))


from biokbase.ServiceWizard.Impl import ServiceWizard

#[ServiceWizard]
#kbase-endpoint = {{ kbase_endpoint }}
#job-service-url = {{ job_service_url }}
#workspace-url = {{ workspace_url }}
#shock-url = {{ shock_url }}
#handle-service-url = {{ kbase_endpoint }}/handle_service
#scratch = /kb/module/work/tmp
#catalog-url = 
#docker-registry-url = 
#rancher-env-url = 
#access-key = 
#secret-key = 
#nginx-port = 443


config = {
    'rancher-compose-bin':testdir+'/../bin/rancher-compose',
    'rancher-env-url':'http://192.168.99.100:8080',
    'catalog-url':'https://ci.kbase.us/services/catalog',
    'temp-dir':testdir+'/temp',
    'access-key':'060C6418C80CE7D08D11',
    'secret-key':'KJMHgfSCNWn1cvohPfj6CjzXL6oDzq8RAN5H3fyv',
    'kbase-endpoint':'https://ci.kbase.us/services'
}

ctx = {'token':'asdf', 'user_id':'msneddon'}

wiz = ServiceWizard(config)
print('========')
print(wiz.version(ctx))


status = wiz.start(ctx,{'module_name':'helloservice','version':'beta'})[0]
pprint(status)



log = wiz.get_service_log(ctx, {'instance_id': '1i82', 'service': {'module_name':'helloservice','version':'beta'} })[0]
pprint(log)



ws = wiz.get_service_log_web_socket(ctx, {'instance_id': '1i82', 'service': {'module_name':'helloservice','version':'beta'} })[0]
pprint(ws)



