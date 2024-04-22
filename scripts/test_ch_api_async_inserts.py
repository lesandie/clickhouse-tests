import json
import os
import time

import requests

# export CH_API_HOST="http://localhost:8123"
CH_API_HOST = os.environ["CH_API_HOST"]


def api_async_insert_rows(
    user: str, password: str, database: str, table: str, file: str
):
    """
    Insert using async INSERTs
    Use scripts/DDL.sql to generate a dataset.json file
    use JSONEachRow and replace newline char for ,
    INSERT INTO table FORMAT JSONEachRow {"a":1, "b":2}, {"c":3, "d":4}
    """
    try:
        if not os.path.isfile(file):
            raise ValueError("File does not exist!")

        url = f"{CH_API_HOST}"
        batch = []
        headers = {"Content-type": "text/json"}
        params = {
            "user": f"{user}",
            "password": f"{password}",
            "async_insert": 1,
            "wait_for_async_insert": 1,
            "async_insert_max_query_number": 200,  # max queries to flush
            "async_insert_busy_timeout_ms": 5000,  # 5 secs to flush
        }

        # Use data instead of inlining in params
        with open(file, "r") as f:
            for line in f:
                if len(batch) < 5:
                    batch.append(line.replace("\n", ","))
                else:
                    rows = ""
                    for value in batch:
                        rows = rows + value

                    batch.clear()
                    params["query"] = (
                        f"INSERT INTO {database}.{table} FORMAT JSONEachRow {rows[:-1]}"
                    )

                    start_time = time.monotonic()
                    response = requests.post(
                        url, headers=headers, params=params, verify=False
                    )

                    response_dict = dict(response.headers)
                    response_dict["status_code"] = str(response.status_code)
                    response_dict["ack_time"] = time.monotonic() - start_time
                    print(json.dumps(response, indent=2))

    except Exception as e:
        print(e)


if __name__ == "__main__":
    api_async_insert_rows(
        user="default",
        password="",
        database="default",
        table="insert_test",
        file="/tmp/file.json",
    )
