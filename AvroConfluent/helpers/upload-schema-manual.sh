# Check schema
kafkacat -b localhost:9092  -C -t sensor-topic -o beginning -f '%s' -c 3 | clickhouse-local --input-format AvroConfluent --format_avro_schema_registry_url 'http://localhost:8081/subjects/sensor_data' -S "timestamp Int64, identifier String, value UInt64" -q 'select * from sensor_data'


# sensor schema manual upload using schema registry api
curl -s \
-X POST \
"http://localhost:8081/subjects/sensor-value/versions" \
-H "Content-Type: application/vnd.schemaregistry.v1+json" \
-d '{"schema": "{\"type\":\"record\",\"name\":\"sensor_sample\",\"fields\":[{\"name\":\"timestamp\",\"type\":\"long\"},{\"name\":\"identifier\",\"type\":\"string\"},{\"name\":\"value\",\"type\":\"long\"}]}"}' \
| jq
