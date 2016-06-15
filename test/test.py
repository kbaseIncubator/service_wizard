
from pprint import pprint
import os
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
    'access-key':'D74D918EBDC9375CF6B8',
    'secret-key':'jsnTpDmU2qsvyC8o55NtcjhcL4sft4Akf1nxC3Fj'
}

ctx = {'token':'asdf'}

wiz = ServiceWizard(config)
print('========')
print(wiz.version(ctx))


wiz.start(ctx,{'module_name':'onerepotest','version':'dev'})
status = wiz.get_service_status(ctx,{'module_name':'onerepotest','version':'dev'})
pprint(status)