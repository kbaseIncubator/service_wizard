# url, access and secrete key can also be represented in Env variables
# the following command assumes docker-compose.yml and rancher-compose.yml in the working directory
# The most of behavior is quite similar to docker-compose with few exceptions
rancher-compose --url http://docker02.berkeley.kbase.us:8888/v1/projects/1a5 --access-key 7EDD9F726F251CF2DF27 --secret-key YYYYYYYYY  -p MyProjectName --verbose  up
