#!/bin/sh

set -e

FLECTRA_CONFIGURATION_DIR=/etc/flectra
FLECTRA_CONFIGURATION_FILE=$FLECTRA_CONFIGURATION_DIR/flectra.conf
FLECTRA_DATA_DIR=/var/lib/flectra
FLECTRA_GROUP="flectra"
FLECTRA_LOG_DIR=/var/log/flectra
FLECTRA_LOG_FILE=$FLECTRA_LOG_DIR/flectra-server.log
FLECTRA_USER="flectra"

if [ -d /usr/lib/python3.7 ]; then
    SITE_PACK_DIR37=/usr/lib/python3.7/site-packages
    [[ ! -d ${SITE_PACK_DIR37} ]] && mkdir -p ${SITE_PACK_DIR37}
    ln -s /usr/lib/python3.6/site-packages/flectra ${SITE_PACK_DIR37}/flectra
fi

if ! getent passwd | grep -q "^flectra:"; then
    groupadd $FLECTRA_GROUP
    adduser --system --no-create-home $FLECTRA_USER -g $FLECTRA_GROUP
fi
# Register "$FLECTRA_USER" as a postgres user with "Create DB" role attribute
su - postgres -c "createuser -d -R -S $FLECTRA_USER" 2> /dev/null || true
# Configuration file
mkdir -p $FLECTRA_CONFIGURATION_DIR
# can't copy debian config-file as addons_path is not the same
if [ ! -f $FLECTRA_CONFIGURATION_FILE ]
then
    echo "[options]
; This is the password that allows database operations:
; admin_passwd = admin
db_host = False
db_port = False
db_user = $FLECTRA_USER
db_password = False
addons_path = /usr/lib/python3.6/site-packages/flectra/addons
" > $FLECTRA_CONFIGURATION_FILE
    chown $FLECTRA_USER:$FLECTRA_GROUP $FLECTRA_CONFIGURATION_FILE
    chmod 0640 $FLECTRA_CONFIGURATION_FILE
fi
# Log
mkdir -p $FLECTRA_LOG_DIR
chown $FLECTRA_USER:$FLECTRA_GROUP $FLECTRA_LOG_DIR
chmod 0750 $FLECTRA_LOG_DIR
# Data dir
mkdir -p $FLECTRA_DATA_DIR
chown $FLECTRA_USER:$FLECTRA_GROUP $FLECTRA_DATA_DIR

INIT_FILE=/lib/systemd/system/flectra.service
touch $INIT_FILE
chmod 0700 $INIT_FILE
cat << EOF > $INIT_FILE
[Unit]
Description=Flectra Open Source ERP and CRM
After=network.target

[Service]
Type=simple
User=flectra
Group=flectra
ExecStart=/usr/bin/flectra --config $FLECTRA_CONFIGURATION_FILE --logfile $FLECTRA_LOG_FILE
KillMode=mixed

[Install]
WantedBy=multi-user.target
EOF
