import json
from uuid import uuid4

from confluent_kafka import Producer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import (
    MessageField,
    SerializationContext,
    StringSerializer,
)

BOOTSTRAP_ADDRESS = "localhost:9092"
TOPIC_NAME = "sensor-topic"
SCHEMA_FILE = "sensor_schema.avsc"
SCHEMA_REGISTRY_URL = "http://localhost:8081"
JSON_DATA = "sensor_data.jsonl"

# Create a Kafka client ready to produce messages
producer_conf = {"bootstrap.servers": BOOTSTRAP_ADDRESS}
producer = Producer(producer_conf)

# Get the schema to use to serialize the message, string
with open(SCHEMA_FILE, "r") as f:
    schema = f.read()
print(schema)

# Init the Schema registry. No need to upload schema.
# wil create a schema in the registry named TOPIC_NAME-value
schema_registry_conf = {"url": SCHEMA_REGISTRY_URL}
schema_registry_client = SchemaRegistryClient(schema_registry_conf)

# Init the serializer the using the schema and schema registry
avro_serializer = AvroSerializer(schema_registry_client, schema)
# Serializer for message key if needed
string_serializer = StringSerializer("utf_8")

# Serialize messages
with open(JSON_DATA) as f:
    for line in f:
        dict_line = json.loads(line)
        print(dict_line)
        # message key if needed
        # key = (string_serializer(str(uuid4())),)
        key = None
        # headers if needed
        headers = []
        # Send the serialized message to the Kafka topic
        producer.produce(
            topic=TOPIC_NAME,
            value=avro_serializer(
                dict_line, SerializationContext(TOPIC_NAME, MessageField.VALUE)
            ),
            key=key,
            headers=headers,
        )

    producer.flush()  # flush all messages
