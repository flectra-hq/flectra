%global name flectra
%global release 1
%global unmangled_version %{version}
%global __requires_exclude ^.*flectra/addons/mail/static/scripts/flectra-mailgate.py$

Summary: Flectra Server
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{name}-%{unmangled_version}.tar.gz
License: LGPL-3
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Vendor: FlectraHQ, Inc. <info@flectrahq.com>
Requires: sassc
BuildRequires: python3-devel
BuildRequires: pyproject-rpm-macros
Url: https://www.flectrahq.com

%description
Flectra is a complete ERP and CRM. The main features are accounting (analytic
and financial), stock management, sales and purchases management, tasks
automation, marketing campaigns, help desk, POS, etc. Technical features include
a distributed server, an object database, a dynamic GUI,
customizable reports, and XML-RPC interfaces.

%generate_buildrequires
%pyproject_buildrequires

%prep
%autosetup

%build
%py3_build

%install
%py3_install

%post
#!/bin/sh

set -e

FLECTRA_CONFIGURATION_DIR=/etc/flectra
FLECTRA_CONFIGURATION_FILE=$FLECTRA_CONFIGURATION_DIR/flectra.conf
FLECTRA_DATA_DIR=/var/lib/flectra
FLECTRA_GROUP="flectra"
FLECTRA_LOG_DIR=/var/log/flectra
FLECTRA_LOG_FILE=$FLECTRA_LOG_DIR/flectra-server.log
FLECTRA_USER="flectra"

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
addons_path = %{python3_sitelib}/flectra/addons
default_productivity_apps = True
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


%files
%{_bindir}/flectra
%{python3_sitelib}/%{name}-*.egg-info
%{python3_sitelib}/%{name}
