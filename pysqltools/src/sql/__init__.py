"""
Queries Package. Contains everything SQL-Text query related
"""

from pysqltools.src.connection import SQLConnection
from pysqltools.src.sql.insert import generate_insert_query, insert_pandas
from pysqltools.src.sql.query import Query, SQLString, get_queries_from_path
from pysqltools.src.sql.table import Table
