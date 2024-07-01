from .src.connection import SQLConnection
from .src.queries.insert import generate_insert_query, insert_pandas
from .src.queries.query import Query, SQLString


def format_sql(sql: str, **kwargs) -> str:
    query = Query(sql=sql).format(kwargs)
    return query.sql
