# startup rancher
HOST=http://192.168.99.100

docker stop rancher-server > /dev/null 2>&1
docker rm rancher-server > /dev/null 2>&1

printf '\nStarting Rancher Server, please wait.'
docker run -d --restart=always -p 8080:8080 --name rancher-server rancher/server > /dev/null 2>&1
if [ $? -ne 0 ]; then
    docker start rancher-server > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo 'Unable to start up a rancher server. Fail.'
        exit 1
    fi
fi

until $(curl --output /dev/null --silent --head --fail $HOST:8080/v1); do
    printf '.'; sleep 1;
done
printf '\n'


printf '\nRegistering host with Rancher\n'
# 1) first setup the host url- note: not sure where '1as' comes from, but seems to work
curl -H "Content-Type: application/json" \
     -X PUT -d '{"activeValue":null,"id":"1as!api.host","inDb":false,"name":"api.host","source":null,"type":"activeSetting","value":"'$HOST':8080"}' \
     $HOST':8080/v1/activesettings/1as!api.host' > /dev/null 2>&1
# 2) get the project_id
PROJECT_ID=$(curl -s $HOST:8080/v1/projects | python -c 'import json, sys; obj=json.load(sys.stdin);print(obj["data"][0]["id"])')
printf '   PROJECT_ID='$PROJECT_ID'\n'
# 3) create the registration token
curl -X POST $HOST':8080/v1/projects/'$PROJECT_ID'/registrationtokens' > /dev/null 2>&1
# 4) wait for that to propagate and get the registration url
sleep 1
REGISTRATION_URL=$(curl -s $HOST:8080/v1/registrationtokens | python -c 'import json, sys; obj=json.load(sys.stdin);print(obj["data"][0]["registrationUrl"])')
printf '   REGISTRATION_URL='$REGISTRATION_URL'\n'
# 5) start the rancher agent
printf '\nStarting Rancher Agent.\n'
RANCHER_AGENT=$(docker run -d --privileged -v /var/run/docker.sock:/var/run/docker.sock -v /var/lib/rancher:/var/lib/rancher rancher/agent:v1.0.1 $REGISTRATION_URL)
printf $RANCHER_AGENT'\n\n'

printf '\nWaiting for agent to register.'
until $(curl -s $HOST:8080/v1/projects/1a5/hosts | python -c 'import json,sys; o=json.load(sys.stdin); exit(1-len(o["data"]));'); do
    printf '.'; sleep 1;
done
printf '\n'

printf '\nCreate an admin account'
curl -H "Content-Type: application/json" \
     -X POST -d '{"enabled":true,"username":"admin","accessMode":"unrestricted","name":"admin","password":"admin"}' \
     $HOST':8080/v1/localAuthConfigs' > /dev/null 2>&1

printf '\Setup an api key for the admin account'
# Unfortunately, I think this has to be done through the web-ui!!  arg! (unless you can get a web token somehow, use that to make the /v1/apiKey
# POST to create the new api key

# This call would work, if you can get the 
#curl -H "Content-Type: application/json" \
#     -u admin:admin \ # this line doesn't work...
#     -X POST -d '{"accountId":"1a1","created":null,"description":null,"kind":null,"name":null,"removeTime":null,"removed":null,"type":"apikey"}' \
#     $HOST':8080/v1/apiKey'



######
#now, actually start the 

# sync up the libraries
#rsync -av ../lib/biokbase/* pylib/biokbase/. --exclude *.bak-*

#start the service
#export KB_DEPLOYMENT_CONFIG=test-deploy.cfg
#export PYTHONPATH=pylib
#python test.py

#uwsgi --master --processes 1 --threads 2 --http :5000 --wsgi-file pylib/biokbase/ServiceWizard/Server.py



printf '\nStopping Rancher Server and removing the container.\n'
#docker stop rancher-server > /dev/null 2>&1
#docker rm rancher-server > /dev/null 2>&1

printf 'Stopping Rancher Agent and removing the container.\n'
#docker stop $RANCHER_AGENT > /dev/null 2>&1
#docker rm $RANCHER_AGENT > /dev/null 2>&1



printf '\n'






