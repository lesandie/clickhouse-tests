
# Producer
docker run --network altinity_default \
           --volume /home/dnieto/altinity/docker/kafka-kerberos/configs/secrets:/tmp \
           --env KRB5_CONFIG=/tmp/krb5.conf \
           confluentinc/cp-kafkacat \
           kafkacat -P -b 'cp-kafka:9093' -t tests -d all -L \
            -X security.protocol=SASL_PLAINTEXT \
            -X sasl.mechanism=GSSAPI \
            -X sasl.kerberos.service.name=kafka \
            -X sasl.kerberos.keytab='/tmp/clickhouse.keytab' \
            -X sasl.kerberos.principal='kafka/user1@ALTINITY.TEST'

# Consumer

docker run --network altinity_default \
           --volume /home/dnieto/altinity/docker/kafka-kerberos/configs/secrets:/tmp \
           --env KRB5_CONFIG=/tmp/krb5.conf \
           confluentinc/cp-kafkacat \
           kafkacat -C -b 'cp-kafka:9093' -t tests -f 'Topic %t[%p], offset: %o, key: %k, payload: %S bytes: %s\n' -d all -L \
            -X security.protocol=SASL_PLAINTEXT \
            -X sasl.mechanism=GSSAPI \
            -X sasl.kerberos.service.name=kafka \
            -X sasl.kerberos.keytab='/tmp/clickhouse.keytab' \
            -X sasl.kerberos.principal='user1@ALTINITY.TEST'