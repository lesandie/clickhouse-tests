import os
import subprocess

CH_HOST = os.environ["CH_HOST"]


def check_filepath(filepath) -> bool:
    """
    Checks if the input path is correct and a file exists
    """
    if os.path.isfile(filepath):
        return True
    else:
        return False


def clickhouse_client(host: str, port: str, query: str, input_file: str) -> None:

    if check_filepath(input_file):
        try:
            command = f'/usr/bin/cat {input_file} | /usr/bin/clickhouse-client --host {host} --port {port} --query="{query}"'
            result = subprocess.run(
                command,
                shell=True,
                check=True,
            )
            return print(result.args, result.stderr, result.stdout, result.returncode)
        except subprocess.CalledProcessError as err:
            return print(err.args, err.stderr, err.stdout, err.returncode)
    else:
        return print("File does not exist")


if __name__ == "__main__":

    input_file = "../csv/fact_sales_withnames.csv"
    host = CH_HOST
    port = "9000"
    query = "INSERT INTO tests.insert_test FORMAT CSVWithNames"

    clickhouse_client(host=host, port=port, query=query, input_file=input_file)
