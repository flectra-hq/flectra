#Partially from Odoo's dockerfile
#github.com/odoo/docker

ARG BASE_IMAGE
FROM ${BASE_IMAGE}:latest
LABEL maintainer="FlectraHQ <flectra@flectrahq.com>"
LABEL authors="FlectraHQ,Jamotion"

ARG GITLAB_OWNER=flectra
ARG GITLAB_COMMIT=master
ARG ARG_DB_HOST=postgres
ARG ARG_DB_PORT=5432
ARG ARG_DB_USER=flectra
ARG ARG_DB_PASSWORD=flectra

ENV BRANCH=$ARG_BRANCH
ENV HOST=$ARG_DB_HOST
ENV PORT=$ARG_DB_PORT
ENV USER=$ARG_DB_USER
ENV PASSWORD=$ARG_DB_PASSWORD

USER root
RUN mkdir -p /var/log/flectra && \
    chown -R flectra:flectra /var/log/flectra/

RUN locale-gen --purge en_US.UTF-8 && \
    dpkg-reconfigure --frontend=noninteractive locales && \
    echo -e 'LANG="en_US.UTF-8"\nLANGUAGE="en_US:en"\n' > /etc/default/locale

ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en

USER flectra

ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en

RUN cd /opt/flectra && \
    wget -q -O flectra.tar.gz https://gitlab.com/${GITLAB_OWNER}/flectra/-/archive/${GITLAB_COMMIT}/flectra.tar.gz && \
    tar -zxvf flectra.tar.gz flectra-${GITLAB_COMMIT}/flectra-bin flectra-${GITLAB_COMMIT}/flectra flectra-${GITLAB_COMMIT}/addons && \
    cd flectra-${GITLAB_COMMIT} && \
    mv addons/* flectra/addons/ && \
    mv flectra ../. && \
    mv flectra-bin ../. && \
    cd /opt/flectra && \
    rm -rf flectra-${GITLAB_COMMIT}

EXPOSE 7073 7072

ADD entrypoint.sh /opt/flectra/entrypoint.sh

ENTRYPOINT ["/opt/flectra/entrypoint.sh"]
CMD ["flectra"]

