import avro.schema
from avro.datafile import DataFileReader, DataFileWriter
from avro.io import DatumReader, DatumWriter

SCHEMA_FILE = "sensor_schema.avsc"
AVRO_FILE = "sensor_data.avro"
JSON_FILE = "sensor_data.jsonl"

schema = avro.schema.parse(open(SCHEMA_FILE, "rb").read())

writer = DataFileWriter(open(AVRO_FILE, "wb"), DatumWriter(), schema)

with open(JSON_FILE, "r") as f:
    for line in f:
        writer.append(line)
        print(line)

writer.close()

reader = DataFileReader(open("AVRO_FILE", "rb"), DatumReader())

for line in reader:
    print(line)

reader.close()
