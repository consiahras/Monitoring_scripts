#!/bin/sh
# log provisioning

exec 3>&1 4>&2
trap 'exec 2>&4 1>&3' 0 1 2 3
exec 1>/var/log/provision.log 2>&1
set -x

#Enabling the required repository for installation
sudo dnf config-manager --enable ol8_baseos_latest
sudo dnf config-manager --enable ol8_automation ol8_addons ol8_UEKR6 ol8_appstream

# Installing Oracle cloud agent
sudo dnf install -y oracle-cloud-agent
#Enabling firewall rules before installation
#
sudo firewall-cmd --add-service=http --permanent
sudo firewall-cmd --add-service=https --permanent
sudo firewall-cmd --reload

# install olam and vim
#
dnf install vim -y
sudo dnf install oraclelinux-automation-manager-release-el8 -y
sudo dnf install ol-automation-manager -y


# configure redis
#
cat <<EOF | sudo tee -a /etc/redis.conf
unixsocket /var/run/redis/redis.sock
unixsocketperm 775
EOF

# configure database
#
/var/lib/ol-automation-manager/ol-automation-manager-DB-init.sh

# awx deployment
#
su -l awx -s /bin/bash -c "awx-manage migrate; \
awx-manage createsuperuser --username admin --email noreply@netsuite.com --noinput; \
awx-manage create_preload_data; \
awx-manage provision_instance --hostname=localhost; \
awx-manage register_queue --queuename=tower --hostnames=localhost; \
awx-manage setup_managed_credential_types"

# generate SSL cert for nginx
#
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/tower/tower.key -out /etc/tower/tower.crt -subj "/C=US/ST=NC/L=Durham/O=NetSuite/OU=NSAS"

# configure nginx and set the CLUSTER_HOST_ID
#
cat <<EOF | sudo tee /etc/nginx/nginx.conf
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log;
pid /run/nginx.pid;

include /usr/share/nginx/modules/*.conf;

events {
  worker_connections 1024;
 }

http {
  log_format  main  '\$remote_addr - \$remote_user [\$time_local] "\$request" '
                    '\$status \$body_bytes_sent "\$http_referer" '
                    '"\$http_user_agent" "\$http_x_forwarded_for"';

  access_log  /var/log/nginx/access.log  main;

  sendfile            on;
  tcp_nopush          on;
  tcp_nodelay         on;
  keepalive_timeout   65;
  types_hash_max_size 2048;

      include             /etc/nginx/mime.types;
      default_type        application/octet-stream;
      include /etc/nginx/conf.d/*.conf;
    }
    EOF

    sed -i 's/^CLUSTER_HOST_ID = "awx"/CLUSTER_HOST_ID = "localhost"/g' /etc/tower/settings.py

    # start the OLAM service
    #
    systemctl enable --now ol-automation-manager.service
message: |
  --------------------------------------------------------------------
  Oracle Linux Automation Manager (OLAM) can be accessed by navigating
  to http://localhost in a browser session.

  You can update the admin password by running the shell command:
  --------------------------------------------------------------------
  $ sudo su -l awx -s /bin/bash -c "awx-manage changepassword admin"
  --------------------------------------------------------------------
