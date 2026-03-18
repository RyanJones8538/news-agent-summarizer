import psycopg
import time

"""
Creates connection to the SQL server.
"""
def get_conn(retries=10, delay=2):
    last_error = None
    for _ in range(retries):
        try:
            return psycopg.connect(
                host="db",
                dbname="newsdb",
                user="newsuser",
                password="newspass"
            )
        except Exception as e:
            last_error = e
            time.sleep(delay)
    raise last_error