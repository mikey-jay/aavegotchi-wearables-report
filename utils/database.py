import sqlite3
from datetime import datetime
import pandas as pd

DB_FILE = 'db/wearables-report.db'
MODIFIED_TIME_TABLE_NAME = 'table_modified_time'

def db_connection(func):
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect(DB_FILE)
        result = func(conn, *args, **kwargs)
        conn.close()
        return result
    return wrapper

@db_connection
def get_df_from_database(conn = None, table_name = None) -> pd.DataFrame:
    if conn is None:
        raise ValueError('Database connection is missing')
    return pd.read_sql_query(f"SELECT * FROM {table_name}", conn)

@db_connection
def store_df_to_database(conn = None, table_name = None, df: pd.DataFrame = pd.DataFrame()):
    if conn is None:
        raise ValueError('Database connection is missing')
    if table_name is None:
        raise ValueError('Table name is missing')
    df.to_sql(table_name, conn, if_exists='replace', index=True)
    set_table_modified_now(table_name)

@db_connection
def set_table_modified_now(conn=None, table_name=None):
    if conn is None:
        raise ValueError('Database connection is missing')
    cursor = conn.cursor()
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {MODIFIED_TIME_TABLE_NAME} (table_name TEXT PRIMARY KEY, last_modified TEXT)")
    cursor.execute(f"SELECT last_modified FROM {MODIFIED_TIME_TABLE_NAME} WHERE table_name=?", (table_name,))
    result = cursor.fetchone()
    if result is None:
        cursor.execute(f"INSERT INTO {MODIFIED_TIME_TABLE_NAME} (table_name, last_modified) VALUES (?, datetime('now'))", (table_name,))
    else:
        cursor.execute(f"UPDATE {MODIFIED_TIME_TABLE_NAME} SET last_modified=datetime('now') WHERE table_name=?", (table_name,))
    conn.commit()

@db_connection
def get_table_modified_time(conn=None, table_name=None):
    if conn is None:
        raise ValueError('Database connection is missing')
    cursor = conn.cursor()
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {MODIFIED_TIME_TABLE_NAME} (table_name TEXT PRIMARY KEY, last_modified TEXT)")
    conn.commit()
    try:
        cursor.execute(f"SELECT last_modified FROM {MODIFIED_TIME_TABLE_NAME} WHERE table_name=?", (table_name,))
        result = cursor.fetchone()
        if result is None:
            return datetime.fromtimestamp(0)
        return datetime.strptime(result[0], '%Y-%m-%d %H:%M:%S')
    except sqlite3.Error as e:
        raise ValueError(f"Error getting last modified time for table '{table_name}': {e}")