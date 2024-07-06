from .src.connection import SQLConnection
from .src.SQL.insert import generate_insert_query, insert_pandas
from .src.SQL.query import Query, SQLString
from .src.SQL.table import Table


def format_sql(sql: str, **kwargs) -> str:
    query = Query(sql=sql).format(kwargs)
    return query.sql
