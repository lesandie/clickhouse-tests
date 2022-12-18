# KDC Server Container and Kerberized Kafka service

This container is a simplified version of [docker-kerberos](https://github.com/ist-dsi/docker-kerberos), it provides a standalone KDC server in a docker container, exposing default KDC ports: `749 TCP` and `88 UDP`. The default realm is `ALTINITY.TEST`. Additionally, a default KDC admin principal `kadmin/admin@ALTINITY.TEST` that may be used for KDC functionality testing such as `kadmin` commands.

## Starting

First build the image of the `kdc-server`:

```bash
docker build . -t altinity/kdc-server
```

From the container directory, use `docker-compose up -d` to start all services.

## Kafka usage

The `kdc-server` will be created using some ENV vars located in the `Dockerfile`. Change some of them accordingly to your settings, specially the docker network used (`altinity_default`) if you need to deploy the containers in other network

The `init-script-kdc.sh` will create the basic kerberos service config files (`krb5.conf` and `kdc.conf`) set up some basic principals that will be used by the `zookeeper` and `kafka` services and export various keytabs that also will be used by both zookeeper/kafka and clickhouse.

## General KDC Usage

Once the container started, switch into the container `docker exec -it kdc_server /bin/bash`, and use `kadmin.local` for the KDC amdmin interface. From there you can start adding principals and keytabs using `ktutil`

```bash
ktutil:  addent -password -p myusername@EXAMPLE.COM -k 1 -e RC4-HMAC
Password for myusername@EXAMPLE.COM:
ktutil:  wkt username.keytab
ktutil:  quit
```

After completing those steps there should be a keyfile created in the current directory. That keytab file can be used instead of using a password. For example:

```bash
/usr/bin/kinit myusername@EXAMPLE.COM -k -t /root/username.keytab
```

https://ubuntu.com/server/docs/service-kerberos

## ClickHouse integration

- In the `config.d` there is a `kafka.xml` with all the kafka config parameters. Add files in `config.d` and `users.d` to configure the clickhouse container with custom settings.

- More info:
  - https://github.com/ClickHouse/ClickHouse/tree/master/tests/integration/test_storage_kerberized_kafka

- Create a Kafka engine table and test the kerberos deployment

