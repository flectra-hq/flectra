#Partially from Odoo's dockerfile
#github.com/odoo/docker

FROM registry.gitlab.com/jamotion/flectra/ubuntu_base:latest
LABEL maintainer="FlectraHQ <flectra@flectrahq.com>"
LABEL authors="FlectraHQ,Jamotion"

ARG ARG_BRANCH=master
ARG ARG_DB_HOST=postgres
ARG ARG_DB_PORT=5432
ARG ARG_DB_USER=flectra
ARG ARG_DB_PASSWORD=flectra

ENV BRANCH=$ARG_BRANCH
ENV HOST=$ARG_DB_HOST
ENV PORT=$ARG_DB_PORT
ENV USER=$ARG_DB_USER
ENV PASSWORD=$ARG_DB_PASSWORD

USER flectra
RUN git clone --depth=1 --branch=$BRANCH https://gitlab.com/flectra-hq/flectra.git /opt/flectra/flectra

USER root
RUN mkdir -p /var/log/flectra && \
    chown -R flectra:flectra /var/log/flectra/

USER flectra

EXPOSE 7073 7072

ADD entrypoint.sh /opt/flectra/entrypoint.sh

ENTRYPOINT ["/opt/flectra/entrypoint.sh"]
CMD ["flectra"]

