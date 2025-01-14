FROM ubuntu:18.04
LABEL maintainer="Gigantum <hello@gigantum.com>"

# This is needed for tzdata to proceed, but should probably be set generally
ENV DEBIAN_FRONTEND=noninteractive

# Install system level dependencies
RUN apt-get update && \
    apt-get install -yq --no-install-recommends \
    nginx \
    python3-pip \
    python3-setuptools \
    gosu && \
    apt-get clean

# add mitmproxy to track rstudio
# The latest version of mitmproxy uses the latest cryptography package, but changes the output
# format slightly. Work needed to update this container.
# https://github.com/gigantum/gigantum-client/issues/1714

RUN python3 -m pip install --upgrade pip \
    && pip3 install wheel \
    && pip3 install mitmproxy==5.1.1 \
    && rm -rf /root/.cache
    
# Expose port for nginx
EXPOSE 8079
# Expose port for mitmproxy
EXPOSE 8080

# Overwrite nginx.conf it's our proxy.
COPY nginx.conf /etc/nginx/nginx.conf
COPY rstudio_redirect_patch.py /opt/redirect.py

COPY entrypoint.sh /usr/local/bin/entrypoint.sh
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

CMD ["nginx", "-g", "daemon off;"] 


