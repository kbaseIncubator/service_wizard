FROM kbase/sdkbase2:latest as build


COPY . /tmp/service_wizard
COPY deployment /kb/deployment

RUN cd /tmp && \
    cd /tmp/service_wizard && \
	[ -e deployment/lib ] || mkdir deployment/lib  && \
	[ -e deployment/bin ] || mkdir deployment/bin  && \
    make install-deps deploy-service deploy-server-control-scripts

FROM kbase/kb_python:latest

# These ARGs values are passed in via the docker build command
ARG BUILD_DATE
ARG VCS_REF
ARG BRANCH=develop

COPY --from=build /kb/deployment/ /kb/deployment/
COPY --from=kbase/catalog:latest /kb/deployment/lib /kb/deployment/lib/

ENV KB_DEPLOYMENT_CONFIG /kb/deployment/conf/deployment.cfg

SHELL ["/bin/bash", "-c"]
RUN rm -rf /kb/deployment/jettybase && \
    source activate root && \
    conda install -c anaconda semantic_version && \
    conda install -c conda-forge websocket-client && \
    pip install gdapi && \
    ln -s /usr/lib/python2.7/plat-*/_sysconfigdata_nd.py /usr/lib/python2.7/

# The BUILD_DATE value seem to bust the docker cache when the timestamp changes, move to
# the end
LABEL org.label-schema.build-date=$BUILD_DATE \
      org.label-schema.vcs-url="https://github.com/kbase/service_wizard.git" \
      org.label-schema.vcs-ref=$VCS_REF \
      org.label-schema.schema-version="1.0.0-rc1" \
      us.kbase.vcs-branch=$BRANCH \
      maintainer="Steve Chan sychan@lbl.gov"

ENTRYPOINT [ "/kb/deployment/bin/dockerize" ]
CMD [ "-template", "/kb/deployment/conf/.templates/deployment.cfg.templ:/kb/deployment/conf/deployment.cfg", \
      "/kb/deployment/services/service_wizard/start_service" ]

WORKDIR /kb/deployment/services/service_wizard/

