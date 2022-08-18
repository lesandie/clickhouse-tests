
import click
from kafka import KafkaAdminClient, KafkaProducer
from kafka.admin import NewTopic
from kafka.errors import KafkaError

# Click commands

@click.command()
@click.option(
    "--server",
    help="Kafka server like host:port",
    required=True,
    type=str
)
@click.option(
    "--topic",
    help="Name of the topic",
    required=True,
    type=str
)
@click.option(
    "--file",
    help="File with text messages to send",
    required=True,
    type=click.Path()
)
@click.option(
    "--delay",
    help="Delay in ms until sending to the broker",
    default=1,
    show_default=True,
    required=False,
    type=int
)
@click.option(
    "--batch",
    help="Number of max messages to batch during the delay",
    default=1,
    show_default=True,
    required=False,
    type=int
)
def kafka_producer(server, topic, file, delay, batch):
    """
    Main producer
    """

    try:
        # Create Kafka topic
        producer = KafkaProducer(
            bootstrap_servers=server,
            acks="all",
            # batch settings
            linger_ms=delay,
            batch_size=batch,
        )
        admin = KafkaAdminClient(bootstrap_servers=server)

        if topic not in admin.list_topics():
            new_topic = NewTopic(name=topic, num_partitions=1, replication_factor=1)
            admin.create_topics([new_topic])
            topic = new_topic.name

        with open(file, "r") as f:
            for line in f:
                print(line)
                producer.send(topic=topic, value=line.encode("utf-8"))
                print(f"Produced: {line}")

    except KafkaError as kafka_error:
        print(f"Kafka error: {kafka_error}")
    except Exception as error:
        print(f"General error: {error} ")


if __name__ == "__main__":
    kafka_producer()
