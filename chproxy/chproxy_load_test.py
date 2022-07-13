import concurrent.futures
import json
import logging
import os
from datetime import datetime
import random
from typing import Tuple

import click
import requests
from faker import Faker

# Use
CHPROXY_HOST = os.environ["CHPROXY_HOST"]


def fake_datetime_list(n: int) -> Tuple:
    """
    Generate fake datetime list within a rage
    """
    fake = Faker()
    start = datetime(2020, 10, 1, 0, 0)
    end = datetime(2020, 12, 1, 0, 0)
    return [fake.date_time_between(start_date=start, end_date=end, tzinfo=None) for ts in range(n)]

def api_fetch_rows(timestamp: str) -> str:
    """
    Execute queries via chproxy
    ?param_id=2&param_phrase=test" -d "SELECT * FROM table WHERE int_column = {id:UInt8} and string_column = {phrase:String}"
    Dynamic paramaters not supported in chproxy: github.com/ContentSquare/chproxy/issues/128
    """
    try:
        url = f"{CHPROXY_HOST}"
        headers = {"Content-type": "application/json"}
        params = {
            # "param_timestamp": datetime.strftime(timestamp,"%Y-%m-%d %H:%M:%S"),
            "query": f"SELECT * FROM sales.fact_sales \
                WHERE order_datetime BETWEEN toDateTime('{timestamp}') - INTERVAL 5 MINUTE AND toDateTime('{timestamp}') \
                FORMAT JSON",
            # "buffer_size": "3000000",
            # "wait_end_of_query": 1,
        }

        response = requests.get(url, headers=headers, params=params)

        if response.status_code in (200, 201):
            logging.info(response.status_code, response.json())
            return print(response.status_code), print(
                json.dumps(response.json(), indent=2)
            )
        else:
            logging.error(response.status_code, response.json())
            return print(response.status_code), print(response.json())

    except Exception as error:
        logging.critical(error)
        return error


def api_insert_rows(file: str) -> str:
    """
    Insert using POST in binary format
    """
    try:
        url = f"{CHPROXY_HOST}"
        headers = {"Content-type": "text/csv"}
        # headers = {"Content-Type": "text/tab-separated-values; charset=UTF-8"}
        params = {
            "query": "INSERT INTO test.insert_test \
                (id_a, id_b, id_localizacion_almacen, id_producto, id_seccion, \
                order_type, order_id, order_datetime, unit_price, total) \
                FORMAT CSVWithNames",
            "max_insert_block_size": 1000000,
            "format_csv_allow_single_quotes": 0,
            "format_csv_allow_double_quotes": 0,
        }

        with open(file, "rb") as f:
            response = requests.post(url, headers=headers, params=params, data=f)
            if response.status_code in (200, 201, 204):
                logging.info(response.status_code, response.json())
                return print(json.dumps(response.json(), indent=2))
            else:
                logging.error(response.status_code, response.json())
                return print(response.status_code), print(response.json())
    except Exception as error:
        logging.critical(error)
        return error


# Click commands


@click.group()
@click.pass_context
def cli(ctx):
    pass


@cli.command(
    "load_test",
    help="Init chproxy load concurrent requests",
)
@click.option("--requests", help="number of requests", required=True, type=int)
@click.option("--workers", help="number of concurrent queries", required=True, type=int)
@click.option("--random_ts", help="number of random timestamps to use in WHERE condition", required=True, type=int)
def load_test(requests, workers, random_ts):
    # Set logging level
    logging.basicConfig(
        level=logging.INFO,
        filename="chproxy.log",
        filemode="w",
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    # Init tasks
    tasks = []
    ts_list = fake_datetime_list(random_ts)

    with concurrent.futures.ProcessPoolExecutor() as executor:
        for request in range(requests):
            logging.info(f"Request {request}")
            for x in range(workers):
                timestamp = datetime.strftime(random.choice(ts_list), "%Y-%m-%d %H:%M:%S")
                tasks.append(executor.submit(api_fetch_rows, timestamp))
                logging.info(f"Finished loading task {x}")
            for r in concurrent.futures.as_completed(tasks):
                logging.info(r.result())


@cli.command("insert_test", help="Insert CSV")
@click.option(
    "--file",
    required=True,
    type=click.Path(exists=True),
    help="Input CSV filename for insert",
)
def insert_test(file: str) -> str:
    api_insert_rows(file)


if __name__ == "__main__":
    cli()
