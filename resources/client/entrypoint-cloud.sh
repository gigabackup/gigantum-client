#!/bin/bash

# TODO: Generalize Dev Env Vars
export JUPYTER_RUNTIME_DIR=/mnt/share/jupyter/runtime

# Add local user
# Either use the LOCAL_USER_ID if passed in at runtime or
# fallback
USER_ID=${LOCAL_USER_ID:-9001}

echo "Starting with UID: ${USER_ID}"
useradd --shell /bin/bash -u ${USER_ID} -o -c "" -m giguser
export HOME=/home/giguser

# Set permissions for container-container share
chown -R giguser:root /mnt/share/
chown -R giguser:root /mnt/gigantum/

# Set permissions for demo project
chown giguser:root /opt/my-first-project.zip

# Setup git config for giguser
gosu giguser bash -c "git config --global user.email 'noreply@gigantum.io'"
gosu giguser bash -c "git config --global user.name 'Gigantum Client'"
gosu giguser bash -c "git config --global credential.helper 'cache --timeout 3600'"

# Setup everything to allow giguser to run nginx and git
chown -R giguser:root /opt/log
chown -R giguser:root /opt/nginx
chown -R giguser:root /opt/redis
chown -R giguser:root /opt/run
chown -R giguser:root /opt/gtmcore
chown -R giguser:root /opt/gtmapi
chown -R giguser:root /var/lib/nginx/
chown -R giguser:root /var/log/nginx/
chown --silent giguser:root /var/lock/nginx.lock
chown giguser:root /run/nginx.pid

gosu giguser git lfs install
exec gosu giguser "$@"

