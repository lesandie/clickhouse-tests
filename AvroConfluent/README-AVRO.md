# Using AvroConfluent format with ClickHouse

## Break & Avro

Apache Avro is a row-oriented data serialization framework developed within Apache’s Hadoop project, and uses schemas to specify the structure of the data being encoded. It has two schema languages: one (Avro IDL) intended for human editing, and one (based on JSON) that is more easily machine-readable.

[ClickHouse Avro format](https://clickhouse.com/docs/en/sql-reference/formats/#data-format-avro) supports reading and writing Avro data files.

[AvroConfluent](https://clickhouse.com/docs/en/sql-reference/formats/#data-format-avro-confluent) supports decoding single-object Avro messages commonly used with Kafka and Confluent Schema Registry.

Avro relies on schemas. When Avro data is read, the schema used when writing it is always present. This permits each datum to be written with no per-value overheads, making serialization both fast and small. This also facilitates use with dynamic, scripting languages, since data, together with its schema, is fully self-describing.

When Avro data is stored in a file, its schema is stored with it, so that files may be processed later by any program. If the program reading the data expects a different schema this can be easily resolved, since both schemas are present.

Avro schemas are defined with JSON . This facilitates implementation in languages that already have JSON libraries.

With Avro, when an application wants to encode some data (to write it to a file or database, to send it over the network, etc.), it encodes the data using whatever version of the schema it knows about—for example, that schema may be compiled into the application. This is known as the writer’s schema.

When an application wants to decode some data (read it from a file or database, receive it from the network, etc.), it is expecting the data to be in some schema, which is known as the reader’s schema. That is the schema the application code is relying on—code may have been generated from that schema during the application’s build process.

The key idea with Avro is that the writer’s schema and the reader’s schema don’t have to be the same, they only need to be compatible. When data is decoded (read), the Avro library resolves the differences by looking at the writer’s schema and the reader’s schema side by side and translating the data from the writer’s schema into the reader’s schema. To learn more check [Avro documentation](https://avro.apache.org/docs/1.11.1/)

It is nice that Avro schemas can be packaged in each file/datum/application, but it is often a better architectural pattern to instead register them in an external system and then referenced from each application. This allows the following:

* Decoupling of schemas from producers and consumers
* Potential to upgrade producers without upgrading consumers
* Central location to track all Schemas used in production
* Document the data format required for each topic/queue
* Centralized control of data format (schema) evolution

So, having a Schema registry is convenient to store different schemas from different pipelines/data that can be referenced/checked with an API call. Confluent provides a Schema registry that can be used with Avro, also there are other options like Apicurio Registry or if you're a RedPanda user, then you can use the embedded schema registry that comes with the Redpanda distribution.

In our case we used Redpanda broker, because it is Kafka API compatible it brings the Schema registry in and has a nice Admin console to publish messages, create topics and do the typical admin stuff related to a Kafka broker.

## Helpers

To allow a basic testing environment I created a couple of simple python scripts, to avro serialize & publish messages to a Kafka topic, and another to serialize basic avro messages in a file. You can check them in the [helpers]() folder. They are easy to use, simply change the global variables in capitals to your use case and you're good to go.

## Simple sensor example

This example will showcase a simple sensor use case. The schema is a flat JSON with no nested structures. It will give us a good grasp on how this Avro schema stuff works with ClickHouse. The schema is very simple, 3 fields a timestamp, a name and a value for the measurement. Here the first important thing is to map the avro types to ClickHouse types. You can have a look at the [data type matching section in ClickHouse docs](https://clickhouse.com/docs/en/sql-reference/formats/#data_types-matching).


## Nested trade example

This example will showcase a use case for crypto trading, with a root base trade and some nested trading events. This structure is not very complex also but will show us how a nested structure implemented with arrays, works with Avro and ClickHouse.
