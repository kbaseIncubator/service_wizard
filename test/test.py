
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
    'secret-key':'KJMHgfSCNWn1cvohPfj6CjzXL6oDzq8RAN5H3fyv'
}

ctx = {'token':'asdf'}

wiz = ServiceWizard(config)
print('========')
print(wiz.version(ctx))

import timeit


# check the status of helloservice beta, this should start things up.
print('starting up helloservice - beta by checking status.  DYNAMIC!')
start = timeit.default_timer()
status = wiz.get_service_status(ctx,{'module_name':'helloservice','version':'beta'})[0]
stop = timeit.default_timer()
pprint(status)
if(status['up']!=1): print('!!!!!!!!!!!!!!!!!!!!FAIL!!!!!!!!!!!!!!!!!!!!!!\n\n'); sys.exit(1);
print('took ' + str(stop-start) + 's');

print('====\nchecking status again should be much faster')
start = timeit.default_timer()
status = wiz.get_service_status(ctx,{'module_name':'helloservice','version':'beta'})[0]
stop = timeit.default_timer()
pprint(status)
if(status['up']!=1): print('!!!!!!!!!!!!!!!!!!!!FAIL!!!!!!!!!!!!!!!!!!!!!!\n\n'); sys.exit(1);
print('took ' + str(stop-start) + 's');

print('====\ncalling start service for helloservice -dev')
wiz.start(ctx,{'module_name':'helloservice','version':'dev'})
status = wiz.get_service_status(ctx,{'module_name':'helloservice','version':'dev'})[0]
pprint(status)
if(status['up']!=1): print('!!!!!!!!!!!!!!!!!!!!FAIL!!!!!!!!!!!!!!!!!!!!!!\n\n'); sys.exit(1);

print('====\nlisting status')
status_list = wiz.list_service_status(ctx,{})[0]
pprint(status_list)
for s in status_list:
    if s['module_name']=='HelloService' and 'beta' in s['release_tags']:
        if(s['up']!=1): print('!!!!!!!!!!!!!!!!!!!!FAIL!!!!!!!!!!!!!!!!!!!!!!\n\n'); sys.exit(1);
    if s['module_name']=='HelloService' and 'dev' in s['release_tags']:
        if(s['up']!=1): print('!!!!!!!!!!!!!!!!!!!!FAIL!!!!!!!!!!!!!!!!!!!!!!\n\n'); sys.exit(1);

print('====\nstarting something that is already running should be fine, start and list status again')
status = wiz.start(ctx,{'module_name':'helloservice','version':'dev'})[0]
pprint(status)
if(status['up']!=1): print('!!!!!!!!!!!!!!!!!!!!FAIL!!!!!!!!!!!!!!!!!!!!!!\n\n'); sys.exit(1);


print('====\nshould be able to stop one of them, say dev')
status = wiz.stop(ctx,{'module_name':'helloservice','version':'dev'})[0]
pprint(status)
if(status['up']!=0): print('!!!!!!!!!!!!!!!!!!!!FAIL!!!!!!!!!!!!!!!!!!!!!!\n\n'); sys.exit(1);

print('====\nstatus list should show that just one is stopped')
status_list = wiz.list_service_status(ctx,{})[0]
pprint(status_list)
for s in status_list:
    if s['module_name']=='HelloService' and 'beta' in s['release_tags']:
        if(s['up']!=1): print('!!!!!!!!!!!!!!!!!!!!FAIL!!!!!!!!!!!!!!!!!!!!!!\n\n'); sys.exit(1);
    if s['module_name']=='HelloService' and 'dev' in s['release_tags']:
        if(s['up']!=0): print('!!!!!!!!!!!!!!!!!!!!FAIL!!!!!!!!!!!!!!!!!!!!!!\n\n'); sys.exit(1);

print('====\nstop the other one too')
status = wiz.stop(ctx,{'module_name':'helloservice','version':'beta'})[0]
if(status['up']!=0): print('!!!!!!!!!!!!!!!!!!!!FAIL!!!!!!!!!!!!!!!!!!!!!!\n\n'); sys.exit(1);
status_list = wiz.list_service_status(ctx,{})[0]
pprint(status_list)
for s in status_list:
    if s['module_name']=='HelloService' and 'beta' in s['release_tags']:
        if(s['up']!=0): print('!!!!!!!!!!!!!!!!!!!!FAIL!!!!!!!!!!!!!!!!!!!!!!\n\n'); sys.exit(1);
    if s['module_name']=='HelloService' and 'dev' in s['release_tags']:
        if(s['up']!=0): print('!!!!!!!!!!!!!!!!!!!!FAIL!!!!!!!!!!!!!!!!!!!!!!\n\n'); sys.exit(1);


print('====\nnow start back up just one')
status = wiz.start(ctx,{'module_name':'helloservice','version':'dev'})[0]
pprint(status)
if(status['up']!=1): print('!!!!!!!!!!!!!!!!!!!!FAIL!!!!!!!!!!!!!!!!!!!!!!\n\n'); sys.exit(1);
status_list = wiz.list_service_status(ctx,{})[0]
pprint(status_list)
for s in status_list:
    if s['module_name']=='HelloService' and 'beta' in s['release_tags']:
        if(s['up']!=0): print('!!!!!!!!!!!!!!!!!!!!FAIL!!!!!!!!!!!!!!!!!!!!!!\n\n'); sys.exit(1);
    if s['module_name']=='HelloService' and 'dev' in s['release_tags']:
        if(s['up']!=1): print('!!!!!!!!!!!!!!!!!!!!FAIL!!!!!!!!!!!!!!!!!!!!!!\n\n'); sys.exit(1);

print('====\startup the other one too')
status = wiz.start(ctx,{'module_name':'helloservice','version':'beta'})[0]
pprint(status)
if(status['up']!=1): print('!!!!!!!!!!!!!!!!!!!!FAIL!!!!!!!!!!!!!!!!!!!!!!\n\n'); sys.exit(1);
status_list = wiz.list_service_status(ctx,{})[0]
pprint(status_list)
for s in status_list:
    if s['module_name']=='HelloService' and 'beta' in s['release_tags']:
        if(s['up']!=1): print('!!!!!!!!!!!!!!!!!!!!FAIL!!!!!!!!!!!!!!!!!!!!!!\n\n'); sys.exit(1);
    if s['module_name']=='HelloService' and 'dev' in s['release_tags']:
        if(s['up']!=1): print('!!!!!!!!!!!!!!!!!!!!FAIL!!!!!!!!!!!!!!!!!!!!!!\n\n'); sys.exit(1);





