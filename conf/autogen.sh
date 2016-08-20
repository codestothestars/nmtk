#!/bin/bash
# Script to autogenerate a set of keys.
#
# If you are running the server with a self signed certificate, you need
# to create a set of certificates.  This script does that quickly and 
# easily.  Run it and rejoice!
#
#
SERVER_NAME=$(hostname --fqdn)
DIR=$(dirname $0)
pushd $DIR &> /dev/null

openssl req -nodes -x509 -newkey rsa:4096 -keyout ${SERVER_NAME}.key \
            -out ${SERVER_NAME}.crt -days 3650

popd &> /dev/null
