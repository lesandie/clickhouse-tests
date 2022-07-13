import json
import os
from typing import Tuple

import requests

CH_API_HOST = os.environ["CH_API_HOST"]


def check_filepath(filepath) -> bool:
    """
    Checks if the input path is correct and a file exists
    """
    if os.path.isfile(filepath):
        return True
    else:
        print("File does not exist!: enter the correct path")
        return False


def api_fetch_rows(timestamp: str) -> tuple[None, None] | Exception:
    """
    Execute queries via the API using buffering
    """
    try:
        url = f"{CH_API_HOST}"
        headers = {"Content-type": "application/json"}
        # ?param_id=2&param_phrase=test" -d "SELECT * FROM table WHERE int_column = {id:UInt8} and string_column = {
        # phrase:String}"
        params = {
            "param_timestamp": f"{timestamp}",
            "query": "SELECT * FROM default.insert_test \
                WHERE fecha_hora_pedido BETWEEN toDateTime({timestamp:DateTime}) - INTERVAL 5 minute AND toDateTime({timestamp:DateTime}) \
                FORMAT JSON",
            "buffer_size": "3000000",
            "wait_end_of_query": 1,
        }

        response = requests.get(url, headers=headers, params=params)

        if response.status_code in (200, 201):
            return print(response.headers), print(json.dumps(response.json(), indent=2))
        else:
            return print(response.status_code), print(response.content)

    except Exception as e:
        return e


def api_insert_rows(file: str) -> None | tuple[None, None] | Exception:
    """
    Insert using POST in binary format
    """
    try:
        if check_filepath(file):
            url = f"{CH_API_HOST}"
            headers = {"Content-type": "text/csv"}
            #  headers = {"Content-Type": "text/tab-separated-values; charset=UTF-8"}
            params = {
                "query": 'INSERT INTO default.insert_test \
                    (id_order, id_plat, id_warehouse, id_product, order_type, order_status, \
                    datetime_order, units, total) FORMAT CSVWithNames',
                "max_insert_block_size": 1000000,
                "format_csv_allow_single_quotes": 0,
                "format_csv_allow_double_quotes": 0,
            }

            with open(file, 'rb') as f:
                response = requests.post(url, headers=headers, params=params, data=f)
                if response.status_code in (200, 201, 204):
                    return print(json.dumps(response.json(), indent=2))
                else:
                    return print(response.status_code), print(response.content)
        else:
            raise Exception("File does not exist!")
    except Exception as e:
        return e


if __name__ == "__main__":

    api_fetch_rows(timestamp="2021-11-26 00:00:00")
    api_insert_rows(file="../csv/fact_sales_withnames.csv")
