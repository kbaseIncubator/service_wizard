
from pprint import pprint

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
    'rancher-env-url':'http://192.168.99.100:8080',
    'catalog-url':'https://ci.kbase.us/services/catalog',
    'temp-dir':'temp',
    'access-key':'',
    'secret-key':''
}

ctx = {'token':'asdf'}

wiz = ServiceWizard(config)
print('========')
print(wiz.version(ctx))


wiz.start(ctx,{'module_name':'onerepotest','version':'dev'})