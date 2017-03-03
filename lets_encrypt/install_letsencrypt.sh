#!/bin/bash
# A script to install certificates using acme-tiny and Let's Encrypt
# certificates.  This includes the associated cron jobs.  The related code
# is all in the Let's Encrypt subdirectory already.

   pushd $(dirname "$0") &> /dev/null
   LEDIR=$(pwd)
   # Load the NMTK Config for this site.
   source ../.nmtk_config
   cd ..
   NMTK_INSTALL_PATH="$(pwd)"
   popd &> /dev/null

   sudo a2dissite ${NMTK_NAME}.conf
   ACCOUNT_KEY="${HOSTN}_account.key"
   DOMAIN_KEY="${HOSTN}.key"
   DOMAIN_CSR="${HOSTN}.csr"
   CONF_FILE="${NMTK_INSTALL_PATH}/lets_encrypt/lets_encrypt.conf"
   CHALLENGE_DIR="${NMTK_INSTALL_PATH}/htdocs/.well-known/acme-challenge/"
   APACHE_CONF_FILE="/etc/apache2/sites-available/${NMTK_NAME}_le.conf"
   CERTIFICATE_FILE="${NMTK_INSTALL_PATH}/conf/${HOSTN}.crt"
   CERTIFICATE_KEY="${NMTK_INSTALL_PATH}/conf/${HOSTN}.key"
   CERTIFICATE_CHAIN="${NMTK_INSTALL_PATH}/conf/bundle.crt"
   
   # Change to install path/lets encrypt directory
   pushd "${LEDIR}" &> /dev/null
   
   # clone the repo
   if [ ! -d acme-tiny ]; then
      git clone git@github.com:diafygi/acme-tiny.git
   fi
   
   # If we don't have one already there, generate an account key
   if [ -f "${ACCOUNT_KEY}" ]; then
     echo "Using existing account key (${ACCOUNT_KEY})"
   else
     echo "Generating new account key ${ACCOUNT_KEY}"
     openssl genrsa 4096 > "$ACCOUNT_KEY"
   fi
   if [ -f "${DOMAIN_KEY}" ]; then
     echo "Using existing domain key for ${HOSTN}"
   else
     echo "Generating new domain key for ${HOSTN}"
     openssl genrsa 4096 > "${DOMAIN_KEY}"
   fi
   
   cp "${DOMAIN_KEY}" "${CERTIFICATE_KEY}"
   
   # Ensure that scripts cannot read the key.
   sudo chown root "${CERTIFICATE_KEY}"
   
   
   
   if [ -f "${DOMAIN_CSR}" ]; then
     echo "Using existing domain CSR (presumably for ${HOSTN})"
   else 
     echo "Generating new CSR for ${HOSTN}"
     openssl req -new -sha256 -key ${HOSTN}.key -subj "/CN=${HOSTN}" > "${DOMAIN_CSR}"
   fi
   
   # Create the acme-challenge directory:
   mkdir -p $NMTK_INSTALL_PATH/htdocs/.well-known/acme-challenge
   
   
   # Install the apache configuration for lets encrypt
   sed -e 's|NMTK_INSTALL_PATH|'${NMTK_INSTALL_PATH}'|g' \
       -e 's|EMAIL|'${EMAIL}'|g' \
       -e 's|HOSTNAME|'${HOSTN}'|g' \
       -e 's|NMTK_NAME|'${NMTK_NAME}'|g' \
       -e 's|CHALLENGE_DIR|'${CHALLENGE_DIR}'|g' \
       ${CONF_FILE} > apache_conf_file.tmp
  sudo cp apache_conf_file.tmp ${APACHE_CONF_FILE}
  rm apache_conf_file.tmp
  
  sudo a2ensite $(basename ${APACHE_CONF_FILE})
  
  sudo /etc/init.d/apache2 restart
  popd &> /dev/null 
 
  # Copy over the sudoers file so that the www-data user can restart
  # apache in renew_cert.sh (no root needed.)
  sudo cp ${LEDIR}/apache-reload.sudoers /etc/sudoers.d/apache-reload-letsencrypt
 
  # Now generate the certificate.
  bash ${NMTK_INSTALL_PATH}/lets_encrypt/renew_cert.sh
  
  
  # Now install the cron job to renew.
  
  for FILE in "cert_renewal_letsencrypt.cron"; do
    DEST_FILENAME="/etc/cron.d/$(basename ${FILE%.cron})_${NMTK_NAME}"
    sudo -s -- <<EOF
    sed -e 's|NMTK_INSTALL_PATH|'${NMTK_INSTALL_PATH}'|g' \
        -e 's|NMTK_NAME|'${NMTK_NAME}'|g' \
        $FILE > $DEST_FILENAME
EOF
    echo "Created new cron job for $(basename $FILE)"
  done
  
