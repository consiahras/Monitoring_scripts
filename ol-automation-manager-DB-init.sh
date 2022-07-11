#!/bin/bash
if [ $USER != "root" ]; then
    echo "Script must be run as root user"
    exit 1
fi
if ! rpm -q --quiet postgresql-server
then
    "Please install package postgresql-server"
fi
if [ $(ls -A "/var/lib/pgsql/data" 2> /dev/null | wc -l) -eq 0 ]
then
    postgresql-setup --initdb
fi
systemctl start postgresql
su - postgres -c "createuser -S awx" > /dev/null 2>&1
su - postgres -c "createdb -O awx awx" >/dev/null 2>&1
if [ $(su - postgres -c "psql -l |grep awx" | wc -l ) -eq 1 ]
then
    echo "Database pre-setup is completed"
    exit 0
else
    echo    "       Something went wrong during the process of Database setup:
        Please execute each of the steps manually and fix the errors, if there are any:
        dnf install postgresql-server
        systemctl start postgresql
        postgresql-setup --initdb
        su - postgres -c \"createuser -S awx\"
        su - postgres -c \"createdb -O awx awx\"
        "
    exit 1
fi
