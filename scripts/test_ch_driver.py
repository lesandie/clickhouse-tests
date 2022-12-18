import os
from csv import DictReader
from datetime import datetime
from typing import Generator, List

from clickhouse_driver import Client

CH_HOST = os.environ["CH_HOST"]


def iter_csv(filepath: str) -> Generator:
    """
    Generator with the rows of the csv file converted to Python types
    """
    if os.path.isfile(filepath):
        converters = {
        "id_order": int,
        "id_plat": int,
        "id_warehouse": int,
        "id_product": int,
        "order_type": str,
        "order_status": str,
        "datetime_order": lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S"),
        "units": int,
        "total": float,
    }
        with open(filepath, "r") as fd:
            reader = DictReader(fd)
            for line in reader:
                yield {
                    k: (converters[k](v) if k in converters else v) for k, v in line.items()
                }
    else:
        print("File does not exist!: enter the correct path")


def native_insert_rows(filepath: str) -> List | None:
    """
    Insert using native driver
    Alternative with URL client = Client.from_url("clickhouse://localhost:9000/default")
    """
    try:
        if os.path.isfile(filepath):
            client = Client(host=CH_HOST, user="default", password="", port="9000")
            return client.execute(
                "INSERT INTO insert_test VALUES",
                iter_csv(filepath),
            )
        else:
            raise ValueError("File does not exist!")
    except Exception as e:
        print(e)


def native_fetch_rows() -> List | None:
    """
    Insert using native driver
    """
    try:
        client = Client(host=CH_HOST, port=9000, user="default", password="")
        return client.execute("SELECT * FROM insert_test LIMIT 100")
    except Exception as e:
        print(e)


if __name__ == "__main__":

    native_insert_rows(filepath="../fixtures/fact_sales_100k_withnames.csv")
    native_fetch_rows()