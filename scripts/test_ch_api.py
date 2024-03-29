import json
import os

import requests

CH_API_HOST = os.environ["CH_API_HOST"]


def api_fetch_rows(timestamp: str) -> str | None:
    """
    Execute queries via the API using buffering
    """
    try:
        url = f"{CH_API_HOST}"
        headers = {"Content-type": "application/json"}
        # ?param_id=2&param_phrase=test" -d "SELECT * FROM table WHERE int_column = {id:UInt8} and string_column = {phrase:String}"
        params = {
            "param_timestamp": f"{timestamp}",
            "query": "SELECT * FROM default.insert_test \
                WHERE datetime_order BETWEEN toDateTime({timestamp:DateTime}) - INTERVAL 5 minute AND toDateTime({timestamp:DateTime}) \
                FORMAT JSON",
            "max_result_bytes": "4000000",
            "buffer_size": "3000000",
            "wait_end_of_query": 1,
            "send_progress_in_http_headers": 1,  # sending progress will help the network middleware to keep alive the connection, by updating the packet TTL.
            "http_headers_progress_interval_ms": 10000,  # Do not send HTTP headers X-ClickHouse-Progress more frequently than at each specified interval.
        }

        response = requests.get(url, headers=headers, params=params)

        response_dict = dict(response.headers)
        response_dict["status_code"] = str(response.status_code)

        return json.dumps(response_dict, indent=2)

    except Exception as e:
        print(e)


def api_insert_rows(file: str) -> str | None:
    """
    Insert using POST in binary format
    """
    try:
        if not os.path.isfile(file):
            raise ValueError("File does not exist!")
        url = f"{CH_API_HOST}"
        headers = {"Content-type": "text/csv"}
        #  headers = {"Content-Type": "text/tab-separated-values; charset=UTF-8"}
        params = {
            "query": "INSERT INTO default.insert_test \
                    (id_order, id_plat, id_warehouse, id_product, order_type, order_status, \
                    datetime_order, units, total) FORMAT CSVWithNames",
            "max_insert_block_size": 1000000,
            "max_insert_threads": 2,
            "format_csv_allow_single_quotes": 0,
            "format_csv_allow_double_quotes": 0,
            "send_progress_in_http_headers": "1",
            "send_progress_in_http_headers": 1,  # sending progress will help the network middleware to keep alive the connection, by updating the packet TTL.
            "http_headers_progress_interval_ms": 10000,  # Do not send HTTP headers X-ClickHouse-Progress more frequently than at each specified interval.
        }

        with open(file, "rb") as f:
            response = requests.post(url, headers=headers, params=params, data=f)

            response_dict = dict(response.headers)
            response_dict["status_code"] = str(response.status_code)

            return json.dumps(response_dict, indent=2)

    except Exception as e:
        print(e)


if __name__ == "__main__":
    result_select = api_fetch_rows(timestamp="2020-10-26 00:00:00")
    result_insert = api_insert_rows(file="./file.csv")
    print(result_select, result_insert)
