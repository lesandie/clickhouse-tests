# Based on https://github.com/ist-dsi/docker-kerberos/blob/master/kdc-kadmin/init-script.sh
# by Simão Martins and David Duarte
#!/bin/bash
echo "==================================================================================="
echo "==== Kerberos KDC and Kadmin ======================================================"
echo "==================================================================================="
ADMIN_PRINCIPAL_FULL=$KADMIN_PRINCIPAL@$REALM

echo "REALM: $REALM"
echo "ADMIN_PRINCIPAL_FULL: $ADMIN_PRINCIPAL_FULL"
echo "KADMIN_PRINCIPAL: $KADMIN_PRINCIPAL"
echo "ADMIN_PASSWORD: $ADMIN_PASSWORD"
echo ""

echo "==================================================================================="
echo "==== /etc/krb5.conf ==============================================================="
echo "==================================================================================="
KDC_ADMIN_SERVER=$(hostname -f)
tee /etc/krb5.conf <<EOF
[logging]
    default = FILE:/var/log/krb5libs.log
    kdc = FILE:/var/log/krb5kdc.log
    admin_server = FILE:/var/log/kadmind.log
[libdefaults]
    default_realm = $REALM
    dns_lookup_realm = false
    dns_lookup_kdc = true
    forwardable = true
    # WARNING: We use weaker key types to simplify testing as stronger key types
    # require the enhanced security JCE policy file to be installed. You should
    # NOT run with this configuration in production or any real environment. You
    # have been warned.
    default_tkt_enctypes = rc4-hmac des-cbc-md5 des-cbc-crc des3-cbc-sha1 des3-hmac-sha1
    default_tgs_enctypes = rc4-hmac des-cbc-md5 des-cbc-crc des3-cbc-sha1 des3-hmac-sha1
    permitted_enctypes = rc4-hmac des-cbc-md5 des-cbc-crc des3-cbc-sha1 des3-hmac-sha1
[realms]
    $REALM = {
        kdc = $KDC_ADMIN_SERVER
        admin_server = $KDC_ADMIN_SERVER
    }
[domain_realm]
    .$DOMAIN_REALM = $REALM
    $DOMAIN_REALM = $REALM
EOF
echo ""

echo "==================================================================================="
echo "==== /etc/krb5kdc/kdc.conf ========================================================"
echo "==================================================================================="
tee /etc/krb5kdc/kdc.conf <<EOF
[kdcdefaults]
    kdc_ports = 749, 88
[realms]
    $REALM = {
        acl_file = /etc/krb5kdc/kadm5.acl
        admin_keytab = /etc/krb5kdc/kadm5.keytab
        # WARNING: We use weaker key types to simplify testing as stronger key types
        # require the enhanced security JCE policy file to be installed. You should
        # NOT run with this configuration in production or any real environment. You
        # have been warned.
        master_key_type = des3-hmac-sha1
        supported_enctypes = rc4-hmac des-cbc-md5 des-cbc-crc des3-cbc-sha1 des3-hmac-sha1
        #supported_enctypes = arcfour-hmac:normal des3-hmac-sha1:normal des-cbc-crc:normal des:normal des:v4 des:norealm des:onlyrealm des:afs3
        default_principal_flags = +preauth
    }
EOF
echo ""

# Copy the krb5.conf file to be used by zookeeper/kafka/clickhouse services
rm -f /tmp/secrets/*.keytab
cp /etc/krb5.conf /tmp/secrets/

echo "==================================================================================="
echo "==== /etc/krb5kdc/kadm5.acl ======================================================="
echo "==================================================================================="
tee /etc/krb5kdc/kadm5.acl <<EOF
*/admin@$REALM *
EOF
echo ""

echo "==================================================================================="
echo "==== Creating realm ==============================================================="
echo "==================================================================================="
MASTER_PASSWORD=$(tr -cd '[:alnum:]' < /dev/urandom | fold -w30 | head -n1)
/usr/sbin/kdb5_util -P $MASTER_PASSWORD -r $REALM create -s
echo ""

echo "==================================================================================="
echo "==== Creating default principals in the acl ======================================="
echo "==================================================================================="
echo "Adding $ADMIN_PRINCIPAL_FULL principal"
kadmin.local -q "delete_principal -force $KADMIN_PRINCIPAL/admin"
echo ""
kadmin.local -q "addprinc -pw $KADMIN_PASSWORD $KADMIN_PRINCIPAL/admin"
echo ""

echo "==================================================================================="
echo "==== Creating kafka related principals ============================================"
echo "==================================================================================="
kadmin.local -q "addprinc -randkey zookeeper/cp-zookeeper.${DOMAIN_REALM}@${REALM}"
kadmin.local -q "ktadd -norandkey -k /tmp/secrets/kerberized_zookeeper.keytab zookeeper/cp-zookeeper.${DOMAIN_REALM}@${REALM}"

kadmin.local -q "addprinc -randkey kafka/cp-kafka.${DOMAIN_REALM}@${REALM}"
kadmin.local -q "ktadd -norandkey -k /tmp/secrets/kerberized_kafka.keytab kafka/cp-kafka.${DOMAIN_REALM}@${REALM}"

kadmin.local -q "addprinc -randkey zkclient@${REALM}"
kadmin.local -q "ktadd -norandkey -k /tmp/secrets/zkclient.keytab zkclient@${REALM}"

kadmin.local -q "addprinc -randkey user1@${REALM}"
kadmin.local -q "ktadd -norandkey -k /tmp/secrets/clickhouse.keytab user1@${REALM}"

chmod 644 /tmp/secrets/*.*

# Start the kerberos service
krb5kdc
kadmind -nofork