rsync -av ../lib/biokbase/* pylib/biokbase/. --exclude *.bak-*

#start the service
export KB_DEPLOYMENT_CONFIG=test-deploy.cfg
export PYTHONPATH=pylib
python test.py