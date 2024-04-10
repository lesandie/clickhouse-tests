import asyncio
from concurrent.futures import ThreadPoolExecutor
import clickhouse_connect

# Function to execute a query using clickhouse-connect synchronously
def execute_query_sync(query):
    client = clickhouse_connect.get_client(host='localhost', port='8123', user='default')
    result = client.query(query)
    return result

# Asynchronous wrapper function to run the synchronous function in a thread pool
async def execute_query_async(query):
    loop = asyncio.get_running_loop()
    # Use ThreadPoolExecutor to execute the synchronous function
    with ThreadPoolExecutor() as pool:
        result = await loop.run_in_executor(pool, execute_query_sync, query)
        return result

async def main():
    query = "SELECT * FROM system.query_log LIMIT 10"  # Example query
    result = await execute_query_async(query)
    print(result.first_row)

# Run the async main function
if __name__ == '__main__':
    asyncio.run(main())