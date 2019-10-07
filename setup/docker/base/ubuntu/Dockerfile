FROM ubuntu:bionic

LABEL maintainer="FlectraHQ <flectra@flectrahq.com>"
LABEL authors="FlectraHQ,Jamotion"

ARG POSTGRESQL_VERSION=10

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install wget -y

RUN apt-get update && \
    apt-get install git gnupg2 python3 curl expect-dev node-less \
    python3-pillow python3-lxml python-ldap3 python3-dev python3-pip python3-setuptools python3-passlib \
    postgresql-${POSTGRESQL_VERSION} postgresql-server-dev-${POSTGRESQL_VERSION} \
    fontconfig libxfont2 xfonts-encodings xfonts-utils xfonts-base xfonts-75dpi \
    npm nodejs libldap2-dev libsasl2-dev libxml2-dev libxslt1-dev libjpeg-dev zlib1g-dev libfontconfig1 libmagickwand-dev -y

RUN locale-gen --purge en_US.UTF-8 && \
    dpkg-reconfigure --frontend=noninteractive locales && \
    echo -e 'LANG="en_US.UTF-8"\nLANGUAGE="en_US:UTF-8"\n' > /etc/default/locale

ADD requirements.txt /tmp/requirements.txt

RUN pip3 install --upgrade pip
RUN pip3 install -r /tmp/requirements.txt
RUN npm install -g less less-plugin-clean-css -y

RUN curl -SsLO https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.5/wkhtmltox_0.12.5-1.bionic_amd64.deb && \
    apt-get install -f ./wkhtmltox_0.12.5-1.bionic_amd64.deb

# install CI tools
RUN pip3 install coverage coveralls codecov simplejson pyserial pyyaml unittest2 pyopenssl>=16.2.0 \
                 validate_email zpl2 unidecode shapely-geojson simplejson shapely geojson unidecode \
                 email_validator wand imageio moviepy

RUN addgroup --gid=5500 flectra && adduser --system --uid=5500 --gid=5500 --home=/opt/flectra --shell=/bin/bash flectra

ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en

USER flectra

ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en

USER root