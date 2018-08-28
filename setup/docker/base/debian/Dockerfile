FROM debian:jessie

LABEL maintainer="FlectraHQ <flectra@flectrahq.com>"
LABEL authors="FlectraHQ,Jamotion"

ARG POSTGRESQL_VERSION=9.6

RUN apt-get update && \
    apt-get install wget -y

# adding postgresql debian repo in order to access all available postgresql version
RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - && \
    echo "deb http://apt.postgresql.org/pub/repos/apt/ xenial-pgdg main" > /etc/apt/sources.list.d/pgdg.list

RUN apt-get update && \
    apt-get install git gnupg2 python3 curl expect-dev node-less \
    python3-pillow python3-lxml python-ldap3 python3-dev python3-pip python3-setuptools \
    postgresql-${POSTGRESQL_VERSION} postgresql-server-dev-${POSTGRESQL_VERSION} \
    npm nodejs libldap2-dev libsasl2-dev libxml2-dev libxslt1-dev libjpeg-dev zlib1g-dev libfontconfig1 -y

RUN locale-gen --purge en_US.UTF-8 && \
    dpkg-reconfigure --frontend=noninteractive locales && \
    echo -e 'LANG="en_US.UTF-8"\nLANGUAGE="en_US:en"\n' > /etc/default/locale

ADD requirements.txt /tmp/requirements.txt

RUN pip3 install --upgrade pip
RUN pip3 install -r /tmp/requirements.txt
RUN npm install -g less less-plugin-clean-css -y && \
    ln -s /usr/bin/nodejs /usr/bin/node

RUN curl -o wkhtmltox.deb -SL https://downloads.wkhtmltopdf.org/0.12/0.12.2.1/wkhtmltox-0.12.2.1_linux-trusty-amd64.deb && \
    echo '5c509de79121e96908794ebcb9d16647a9385e1d wkhtmltox.deb' | sha1sum -c - && \
    dpkg --force-depends -i wkhtmltox.deb

# install CI tools
RUN pip3 install coverage coveralls codecov simplejson pyserial pyyaml unittest2 pyopenssl>=16.2.0 && \
    wget -N http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz && \
    gunzip GeoLiteCity.dat.gz && \
    mkdir -p /usr/share/GeoIP/ && \
    mv GeoLiteCity.dat /usr/share/GeoIP/

RUN addgroup --gid=5500 flectra && adduser --system --uid=5500 --gid=5500 --home=/opt/flectra --shell=/bin/bash flectra

ENV LC_ALL=en_US.UTF-8
ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US:en

USER flectra

ENV LC_ALL=en_US.UTF-8
ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US:en

USER root