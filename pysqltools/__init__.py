from .src.connection import SQLConnection
from .src.sql.insert import generate_insert_query, insert_pandas, insert_pandas_threads
from .src.sql.query import Query, SQLString, get_queries_from_path
from .src.sql.table import Table
from .src.sql.delete import delete_from_dataframe


def format_sql(sql: str, **kwargs) -> str:
    query = Query(sql=sql).format(kwargs)
    return query.sql
