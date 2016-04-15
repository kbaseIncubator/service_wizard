SERVICE = service_wizard
SERVICE_CAPS = ServiceWizard
SPEC_FILE = ServiceWizard.spec
URL = https://kbase.us/services/service_wizard
DIR = $(shell pwd)
LIB_DIR = lib
SCRIPTS_DIR = scripts
TEST_DIR = test
LBIN_DIR = bin
TARGET ?= /kb/deployment
EXECUTABLE_SCRIPT_NAME = run_$(SERVICE)_async_job.sh
STARTUP_SCRIPT_NAME = start_server.sh
TEST_SCRIPT_NAME = run_tests.sh
KB_RUNTIME ?= /kb/runtime
JARS_DIR = $(TARGET)/lib/jars
ANT = $(KB_RUNTIME)/ant/bin/ant
TOP_DIR = $(shell python -c "import os.path as p; print(p.abspath('../..'))")
TOP_DIR_NAME = $(shell basename $(TOP_DIR))
GITCOMMIT := $(shell if [ -d .git ]; then git rev-parse --short HEAD; else echo 'NOT_TRACKED_BY_GIT'; fi)
TAGS := $(shell if [ -d .git ]; then git tag --contains $(GITCOMMIT); fi)



.PHONY: test

default: compile build-startup-script build-executable-script build-test-script

compile:
	mkdir -p $(LBIN_DIR)
	kb-sdk compile $(SPEC_FILE) \
		--out $(LIB_DIR) \
		--plclname Bio::KBase::$(SERVICE_CAPS)::Client \
		--jsclname javascript/Client \
		--pyclname biokbase.$(SERVICE_CAPS).Client \
		--javasrc src \
		--java \
		--pysrvname biokbase.$(SERVICE_CAPS).Server \
		--pyimplname biokbase.$(SERVICE_CAPS).Impl;
	touch $(LIB_DIR)/biokbase/__init__.py
	touch $(LIB_DIR)/biokbase/$(SERVICE_CAPS)/__init__.py

install-deps:
	bash deps/rancher-compose.sh
	mkdir -p lib/biokbase
	rsync  -av $(TARGET)/lib/biokbase/__init__.py lib/biokbase/.
	rsync  -av $(TARGET)/lib/biokbase/auth.py lib/biokbase/.
	rsync  -av $(TARGET)/lib/biokbase/log.py lib/biokbase/.
	rsync  -av $(TARGET)/lib/biokbase/nexus lib/biokbase/.
	rsync  -av bin/rancher-compose $(TARGET)/bin


build-executable-script:
	mkdir -p $(LBIN_DIR)
	echo '#!/bin/bash' > $(LBIN_DIR)/$(EXECUTABLE_SCRIPT_NAME)
	echo 'script_dir=$$(dirname "$$(readlink -f "$$0")")' >> $(LBIN_DIR)/$(EXECUTABLE_SCRIPT_NAME)
	echo 'export PYTHONPATH=$$script_dir/../$(LIB_DIR):$$PATH:$$PYTHONPATH' >> $(LBIN_DIR)/$(EXECUTABLE_SCRIPT_NAME)
	echo 'python -u $$script_dir/../$(LIB_DIR)/biokbase/$(SERVICE)/Server.py $$1 $$2 $$3' >> $(LBIN_DIR)/$(EXECUTABLE_SCRIPT_NAME)
	chmod +x $(LBIN_DIR)/$(EXECUTABLE_SCRIPT_NAME)

build-startup-script:
	mkdir -p $(LBIN_DIR)
	mkdir -p $(SCRIPTS_DIR)
	echo '#!/bin/bash' > $(SCRIPTS_DIR)/$(STARTUP_SCRIPT_NAME)
	echo 'script_dir=$$(dirname "$$(readlink -f "$$0")")' >> $(SCRIPTS_DIR)/$(STARTUP_SCRIPT_NAME)
	echo 'export KB_DEPLOYMENT_CONFIG=$$script_dir/../deploy.cfg' >> $(SCRIPTS_DIR)/$(STARTUP_SCRIPT_NAME)
	echo 'export PYTHONPATH=$$script_dir/../$(LIB_DIR):$$PATH:$$PYTHONPATH' >> $(SCRIPTS_DIR)/$(STARTUP_SCRIPT_NAME)
	echo 'uwsgi --master --processes 5 --threads 5 --http :5000 --wsgi-file $$script_dir/../$(LIB_DIR)/biokbase/$(SERVICE)/Server.py' >> $(SCRIPTS_DIR)/$(STARTUP_SCRIPT_NAME)
	chmod +x $(SCRIPTS_DIR)/$(STARTUP_SCRIPT_NAME)

build-test-script:
	echo '#!/bin/bash' > $(TEST_DIR)/$(TEST_SCRIPT_NAME)
	echo 'script_dir=$$(dirname "$$(readlink -f "$$0")")' >> $(TEST_DIR)/$(TEST_SCRIPT_NAME)
	echo 'export KB_DEPLOYMENT_CONFIG=$$script_dir/../deploy.cfg' >> $(TEST_DIR)/$(TEST_SCRIPT_NAME)
	echo 'export KB_AUTH_TOKEN=`cat /kb/module/work/token`' >> $(TEST_DIR)/$(TEST_SCRIPT_NAME)
	echo 'export PYTHONPATH=$$script_dir/../$(LIB_DIR):$$PATH:$$PYTHONPATH' >> $(TEST_DIR)/$(TEST_SCRIPT_NAME)
	echo 'cd $$script_dir/../$(TEST_DIR)' >> $(TEST_DIR)/$(TEST_SCRIPT_NAME)
	echo 'python -u -m unittest discover -p "*_test.py"' >> $(TEST_DIR)/$(TEST_SCRIPT_NAME)
	chmod +x $(TEST_DIR)/$(TEST_SCRIPT_NAME)

deploy: deploy-client deploy-service deploy-server-control-scripts

deploy-service: deploy-python-service

deploy-client:
	mkdir -p $(TARGET)/lib/Bio $(TARGET)/lib/biokbase $(TARGET)/lib/javascript
	rsync -av lib/Bio/* $(TARGET)/lib/Bio/.
	rsync -av lib/biokbase/$(SERVICE_CAPS) $(TARGET)/lib/biokbase/. --exclude *.bak-*
	rsync -av lib/javascript/* $(TARGET)/lib/javascript/.

deploy-python-service:
	bash deps/rancher-compose.sh
	rsync -av bin/rancher-compose $(TARGET)/bin
	rsync -av lib/biokbase/$(SERVICE_CAPS) $(TARGET)/lib/biokbase/. --exclude *.bak-*
	echo $(GITCOMMIT) > $(TARGET)/lib/biokbase/$(SERVICE_CAPS)/$(SERVICE_CAPS).version
	echo $(TAGS) >> $(TARGET)/lib/biokbase/$(SERVICE_CAPS)/$(SERVICE_CAPS).version

# This will setup the deployment services directory for
# this service, which includes start/stop scripts
deploy-server-control-scripts:
	mkdir -p $(TARGET)/services/$(SERVICE)
	cp service/get_kb_config.py $(TARGET)/services/$(SERVICE)/.
	python service/build_server_scripts.py \
		service/start_service.template \
		service/stop_service.template \
		$(SERVICE_CAPS) \
		$(KB_RUNTIME) \
		$(TARGET) \
		$(TARGET)/services/$(SERVICE) \
		$(TARGET)/services/$(SERVICE)
	chmod +x $(TARGET)/services/$(SERVICE)/start_service
	chmod +x $(TARGET)/services/$(SERVICE)/stop_service
	echo $(GITCOMMIT) > $(TARGET)/services/$(SERVICE)/$(SERVICE).version
	echo $(TAGS) >> $(TARGET)/services/$(SERVICE)/$(SERVICE).version
	rsync bin/rancher-compose $(TARGET)/bin



test:
	bash $(TEST_DIR)/$(TEST_SCRIPT_NAME)

test-generic-clients:
	$(ANT) test-generic-clients -Djars.dir=$(JARS_DIR)

clean:
	rm -rfv $(LBIN_DIR)
	
