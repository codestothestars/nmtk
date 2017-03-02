#!/bin/bash
#
# A script to allow NMTK to refresh it's Let's Encrypt certificates via cron
#
pushd $(dirname "$0") &> /dev/null
LEDIR=$(pwd)
# Load the NMTK Config for this site.
source ../.nmtk_config
cd ..
NMTK_INSTALL_PATH="$(pwd)"
popd &> /dev/null

CHALLENGE_DIR="${NMTK_INSTALL_PATH}/htdocs/.well-known/acme-challenge/"
APACHE_CONF_FILE="/etc/apache2/sites-available/${NMTK_NAME}_le.conf"
CERTIFICATE_FILE="${NMTK_INSTALL_PATH}/conf/${HOSTN}.crt"
CERTIFICATE_KEY="${NMTK_INSTALL_PATH}/conf/${HOSTN}.key"
CERTIFICATE_CHAIN="${NMTK_INSTALL_PATH}/conf/bundle.crt"
ACCOUNT_KEY="${LEDIR}/${HOSTN}_account.key"
DOMAIN_CSR="${LEDIR}/${HOSTN}.csr"

python "${LEDIR}/acme-tiny/acme_tiny.py" \
       --account-key "${ACCOUNT_KEY}" \
       --csr "${DOMAIN_CSR}" --acme-dir "${CHALLENGE_DIR}" >  "${CERTIFICATE_FILE}" || exit
wget -O - https://letsencrypt.org/certs/lets-encrypt-x3-cross-signed.pem > ${LEDIR}/intermediate.pem
cat "${CERTIFICATE_FILE}" ${LEDIR}/intermediate.pem > "${CERTIFICATE_CHAIN}"
rm -f ${LEDIR}/intermediate.pem
if [[ ${USER} != "www-data" ]]; then
  sudo chown www-data "${CERTIFICATE_CHAIN}" "${CERTIFICATE_FILE}"
fi
sudo /bin/systemctl reload apache2
