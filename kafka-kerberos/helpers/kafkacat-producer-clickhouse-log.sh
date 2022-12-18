#!/bin/bash
# Producer
# you can also use the python producer scripts located in scripts folder
sudo tail -f /var/log/clickhouse-server-json/clickhouse-server.ndjson | kafkacat -P -b localhost:29092 -t clickhouse -z snappy

# Consumer
kafkacat -C -b localhost:29092 -t clickhouse -f 'Topic %t[%p], offset: %o, key: %k, payload: %S bytes: %s\n'

