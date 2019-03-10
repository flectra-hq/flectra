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
    libpq5 libpq-dev postgresql-${POSTGRESQL_VERSION} postgresql-client-${POSTGRESQL_VERSION} \
    postgresql-contrib-${POSTGRESQL_VERSION} postgresql-server-dev-${POSTGRESQL_VERSION} \
    fontconfig libxfont1 xfonts-encodings xfonts-utils xfonts-base xfonts-75dpi \
    npm nodejs libldap2-dev libsasl2-dev libxml2-dev libxslt1-dev libjpeg-dev zlib1g-dev libfontconfig1 -y

RUN locale-gen --purge en_US.UTF-8 && \
    dpkg-reconfigure --frontend=noninteractive locales && \
    echo -e 'LANG="en_US.UTF-8"\nLANGUAGE="en_US:UTF-8"\n' > /etc/default/locale

ADD requirements.txt /tmp/requirements.txt

RUN pip3 install --upgrade pip
RUN pip3 install passlib
RUN pip3 install -r /tmp/requirements.txt
RUN npm install -g less less-plugin-clean-css -y && \
    ln -s /usr/bin/nodejs /usr/bin/node

RUN curl -o wkhtmltox.tar.xz -SL https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.4/wkhtmltox-0.12.4_linux-generic-amd64.tar.xz \
    && echo '3f923f425d345940089e44c1466f6408b9619562 wkhtmltox.tar.xz' | sha1sum -c - \
    && tar xvf wkhtmltox.tar.xz \
    && cp wkhtmltox/lib/* /usr/local/lib/ \
    && cp wkhtmltox/bin/* /usr/local/bin/ \
    && cp -r wkhtmltox/share/man/man1 /usr/local/share/man/


# install CI tools
RUN pip3 install coverage coveralls codecov simplejson pyserial pyyaml unittest2 pyopenssl>=16.2.0 && \
    wget -N http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz && \
    gunzip GeoLiteCity.dat.gz && \
    mkdir -p /usr/share/GeoIP/ && \
    mv GeoLiteCity.dat /usr/share/GeoIP/

RUN addgroup --gid=5500 flectra && adduser --system --uid=5500 --gid=5500 --home=/opt/flectra --shell=/bin/bash flectra

ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en

USER flectra

ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en

USER root