import os
from csv import DictReader
from datetime import datetime
from typing import Generator

from clickhouse_driver import Client

CH_HOST = os.environ["CH_HOST"]


def check_filepath(filepath) -> bool:
    """
    Checks if the input path is correct and a file exists
    """
    if os.path.isfile(filepath):
        return True
    else:
        print("File does not exist!: enter the correct path")
        return False


def iter_csv(filepath: str) -> Generator:
    """
    Generator with the rows of the csv file converted to Python types
    """
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


def native_insert_rows(filepath: str) -> None:
    """
    Insert using native driver
    """
    try:
        if check_filepath(filepath):
            client = Client(host=CH_HOST, user="default", password="", port="9001")
            # client = clickhouse_driver.from_url("clickhouse://localhost:9001/default")
            result = client.execute(
                'INSERT INTO tests.insert_test VALUES',
                iter_csv(filepath),
            )
            return print(result)
        else:
            raise Exception("File does not exist!")
    except Exception as e:
        return print(e)


def native_fetch_rows() -> None:
    """
    Insert using native driver
    """
    try:
        client = Client(host=CH_HOST, port=9001, user="default", password="")
        # client = Client.from_url("clickhouse://localhost:90010/default")
        result = client.execute("SELECT * FROM sales.fact_sales LIMIT 10")
        return print(result)
    except Exception as e:
        return print(e)


if __name__ == "__main__":

    native_insert_rows(filepath="../csv/fact_sales_withnames.csv")
    native_fetch_rows()
