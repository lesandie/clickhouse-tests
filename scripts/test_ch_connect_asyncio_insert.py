import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, time
import clickhouse_connect
import csv

# environment variables
HOST = "localhost"
PORT = 8123
USER = "default"
PASSWORD = ""
# dictionary for passing settings to ClickHouse
SETTINGS = {
    "session_id": "random-" + "-" + f"{time()}",
    # Add more settings here if needed
    "date_time_input_format": "best_effort",
}


def execute_query_sync(client, query):
    """
    Function to execute a query using clickhouse-connect synchronously
    """
    result = client.query(query, settings=SETTINGS)
    return result


def execute_insert_sync(client):
    """
    Function to execute an insert using clickhouse-connect synchronously:
    https://github.com/ClickHouse/clickhouse-connect/blob/457533df05fa685b2a1424359bea5654240ef971/examples/insert_examples.py
    """

    # Define the CSV file path
    csv_file_path = "file.csv"

    # Open the CSV file and read data
    with open(csv_file_path, mode="r") as file:
        csv_reader = csv.DictReader(file)
        data = [row for row in csv_reader]

    prepared_data = []
    for row in data[1:]:  # Skip the header row
        # Convert the datetime string to a datetime object
        row["datetime_order"] = datetime.strptime(
            row["datetime_order"], "%Y-%m-%d %H:%M:%S"
        )
        prepared_data.append(list(row.values()))

    # Insert the data into the ClickHouse table ... WIP to the reader: do some batching here
    client.insert(
        database="default",
        table="insert_test",
        data=prepared_data,
        column_names=[
            "id_order",
            "id_plat",
            "id_warehouse",
            "id_product",
            "order_type",
            "order_status",
            "datetime_order",
            "units",
            "total",
        ],
        column_type_names=[
            "UInt16",
            "UInt32",
            "UInt64",
            "UInt16",
            "UInt16",
            "String",
            "DateTime",
            "Int16",
            "Float32",
        ],
        settings=SETTINGS,
    )

    result = client.query(
        "SELECT * FROM insert_test ORDER BY datetime_order DESC LIMIT 1"
    )
    return result


async def execute_query_async(client, query):
    """
    Asynchronous wrapper function to run the synchronous function in a thread pool
    """
    loop = asyncio.get_running_loop()
    # Use ThreadPoolExecutor to execute the synchronous function
    with ThreadPoolExecutor() as pool:
        result = await loop.run_in_executor(pool, execute_query_sync, client, query)
        return result


async def execute_insert_async(client):
    """
    Asynchronous wrapper function to run the synchronous function in a thread pool
    """
    loop = asyncio.get_running_loop()
    # Use ThreadPoolExecutor to execute the synchronous function
    with ThreadPoolExecutor() as pool:
        result = await loop.run_in_executor(pool, execute_insert_sync, client)
        return result


async def main():
    client = clickhouse_connect.get_client(
        host=HOST, port=PORT, user=USER, password=PASSWORD, settings=SETTINGS
    )
    query = "SELECT * FROM system.query_log ORDER BY event_time DESC LIMIT 10"  # Example query
    result = await execute_query_async(client, query)
    print("SELECT result", result.first_row)
    result_insert = await execute_insert_async(client)
    print("INSERT result", result_insert.first_row)


# Run the async main function
if __name__ == "__main__":
    asyncio.run(main())
