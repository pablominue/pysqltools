from .src.queries.queries import Query, SQLString


def format_sql(sql: str, **kwargs) -> str:
    query = Query(sql=sql).format(kwargs)
    return query.sql
