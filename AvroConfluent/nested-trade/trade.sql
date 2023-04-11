-- IMPORTANT Without disabling flatten_tuples ... it will not work ... uncomment below

-- SET flatten_nested = 0


CREATE TABLE trade.trade_queue
(
    `tradeIdentifier` Nullable(String),
    `deskFlowId` Nullable(UInt64),
    `timestamp` Nullable(UInt64),
    `baseTradeLevel` Nullable(Float64),
    `genericTradeMap` Map(String, String),
    `genericTradeArr` Nested(`source` String, `epochSeconds` UInt64)

)
ENGINE = Kafka
SETTINGS kafka_broker_list = 'localhost:9092',
        kafka_topic_list = 'nested-topic',
        kafka_group_name = 'test',
        kafka_format = 'AvroConfluent',
        date_time_input_format = 'best_effort',
        format_avro_schema_registry_url = 'http://localhost:8081',
        kafka_handle_error_mode = 'stream',
        input_format_avro_null_as_default = 1,
        input_format_avro_allow_missing_fields = 1,
        input_format_skip_unknown_fields = 1


CREATE TABLE trade.trade_data
(
    `tradeIdentifier` Nullable(String),
    `deskFlowId` Nullable(UInt64),
    `timestamp` Nullable(DateTime64(3)),
    `baseTradeLevel` Nullable(Float64),
    `genericTradeMap` Map(String, String),
    `genericTradeArr` Nested(`source` String, `epochSeconds` UInt64)
)
ENGINE = MergeTree
ORDER BY (identifier, timestamp)
SETTINGS index_granularity = 8192, allow_nullable_key = 1


CREATE MATERIALIZED VIEW trade.trade_mv TO trade.trade_data
AS
SELECT
    `tradeIdentifier`,
    `deskFlowId`,
    `timestamp`,
    `baseTradeLevel`,
    `genericTradeMap`,
    `genericTradeArr`
FROM trade.trade_queue


CREATE MATERIALIZED VIEW trade.kafka_errors
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
FROM trade.trade_queue
WHERE length(_error) > 0
