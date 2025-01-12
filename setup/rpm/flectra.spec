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
Vendor: Flectra S.A. <info@flectra.com>
Requires: sassc
BuildRequires: python3-devel
BuildRequires: pyproject-rpm-macros
Url: https://www.flectra.com

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

ODOO_CONFIGURATION_DIR=/etc/flectra
ODOO_CONFIGURATION_FILE=$ODOO_CONFIGURATION_DIR/flectra.conf
ODOO_DATA_DIR=/var/lib/flectra
ODOO_GROUP="flectra"
ODOO_LOG_DIR=/var/log/flectra
ODOO_LOG_FILE=$ODOO_LOG_DIR/flectra-server.log
ODOO_USER="flectra"

if ! getent passwd | grep -q "^flectra:"; then
    groupadd $ODOO_GROUP
    adduser --system --no-create-home $ODOO_USER -g $ODOO_GROUP
fi
# Register "$ODOO_USER" as a postgres user with "Create DB" role attribute
su - postgres -c "createuser -d -R -S $ODOO_USER" 2> /dev/null || true
# Configuration file
mkdir -p $ODOO_CONFIGURATION_DIR
# can't copy debian config-file as addons_path is not the same
if [ ! -f $ODOO_CONFIGURATION_FILE ]
then
    echo "[options]
; This is the password that allows database operations:
; admin_passwd = admin
db_host = False
db_port = False
db_user = $ODOO_USER
db_password = False
addons_path = %{python3_sitelib}/flectra/addons
default_productivity_apps = True
" > $ODOO_CONFIGURATION_FILE
    chown $ODOO_USER:$ODOO_GROUP $ODOO_CONFIGURATION_FILE
    chmod 0640 $ODOO_CONFIGURATION_FILE
fi
# Log
mkdir -p $ODOO_LOG_DIR
chown $ODOO_USER:$ODOO_GROUP $ODOO_LOG_DIR
chmod 0750 $ODOO_LOG_DIR
# Data dir
mkdir -p $ODOO_DATA_DIR
chown $ODOO_USER:$ODOO_GROUP $ODOO_DATA_DIR

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
ExecStart=/usr/bin/flectra --config $ODOO_CONFIGURATION_FILE --logfile $ODOO_LOG_FILE
KillMode=mixed

[Install]
WantedBy=multi-user.target
EOF


%files
%{_bindir}/flectra
%{python3_sitelib}/%{name}-*.egg-info
%{python3_sitelib}/%{name}
