

CREATE TABLE sensors.sensor_queue
(
    `timestamp` Nullable(DateTime),
    `identifier` Nullable(String),
    `value` Nullable(UInt64)
)
ENGINE = Kafka
SETTINGS kafka_broker_list = 'localhost9092',
        kafka_topic_list = 'sensor-topic',
        kafka_group_name = 'test',
        kafka_format = 'AvroConfluent',
        date_time_input_format = 'best_effort',
        format_avro_schema_registry_url = 'http://localhost:8081',
        kafka_handle_error_mode = 'stream',
        input_format_avro_null_as_default = 1,
        input_format_avro_allow_missing_fields = 1,
        input_format_skip_unknown_fields = 1


CREATE TABLE sensors.sensor_data
(
    `timestamp` Nullable(DateTime64(3)),
    `identifier` Nullable(String),
    `value` Nullable(UInt64)
)
ENGINE = MergeTree
ORDER BY (identifier, timestamp)
SETTINGS index_granularity = 8192, allow_nullable_key = 1

CREATE MATERIALIZED VIEW sensors.sensor_mv TO sensors.sensor_data
AS
SELECT
    toDateTime(timestamp)
    identifier,
    value
FROM sensors.sensor_queue


CREATE MATERIALIZED VIEW sensors.kafka_errors
(
    `topic` String,
    `partition` Int64,
    `offset` Int64,
    `raw` String,
    `error` String
)
ENGINE = MergeTree
ORDER BY (topic, partition, offset)
SETTINGS index_granularity = 8192 AS
SELECT
    _topic AS topic,
    _partition AS partition,
    _offset AS offset,
    _raw_message AS raw,
    _error AS error
FROM sensors.sensor_queue
WHERE length(_error) > 0
