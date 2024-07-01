import time
from datetime import date
from typing import Any, Generator

import pandas as pd
import sqlparse
from rich.progress import Progress

from pysqltools.src.connection import SQLConnection
from pysqltools.src.log import PabLog
from pysqltools.src.queries.query import Query, assign_parameter

lg = PabLog("Insert")


def prepare_value(val: Any) -> Any:
    """
    Format value from Python types to SQL Types
    """
    if isinstance(val, bool):
        return val
    if isinstance(val, dict):
        val = str(val).replace("'", '"')
    if isinstance(val, pd.Timestamp):
        val = "TIMESTAMP '" + str(val) + "'"
    if isinstance(val, date):
        val = "DATE '" + str(val) + "'"
    if isinstance(val, list):
        val = "ARRAY " + str(val)
    if isinstance(val, float):
        val = "DOUBLE '" + str(val) + "'"
    if isinstance(val, int):
        val = "INT '" + str(val) + "'"
    if pd.isnull(val):
        val = "NULL"

    try:
        if (
            "'" in val
            and "DOUBLE" not in val
            and "INT" not in val
            and "TIMESTAMP" not in val
            and "DATE" not in val
        ):
            val = val.replace("'", "''")
    except TypeError:
        lg.log.warning("Not Adding Quotes")

    return val


def join_values(data: list[Any]) -> str:
    """
    Create a String for the VALUES () SQL Syntax
    """
    clean_list = []
    for val in data:
        if isinstance(val, bool):
            val = str(val)
        if (
            isinstance(val, str)
            and "DOUBLE" not in val
            and "INT" not in val
            and "TIMESTAMP" not in val
            and "DATE" not in val
            and "ARRAY" not in val
        ) and val.lower() not in ["true", "false"]:
            val = "'" + val + "'"
        try:
            if "NULL" in val:
                val = "NULL"
        except TypeError:
            lg.log.error("Type not using Nulls")

        clean_list.append(str(val))
    str_data = (", ").join(clean_list)
    return "(" + str_data + ")"


def pandas_to_sql(df: pd.DataFrame) -> Generator[str, None, None]:
    """
    Generator to get one row insert statement
    """
    for row in df.values:
        data_list = [prepare_value(x) for x in row]
        data_string = join_values(data_list)
        yield data_string


def generate_insert_query(
    df: pd.DataFrame, table: str = None, schema: str = None, batch_size: int = 5000
) -> Generator[Query, None, None]:
    if df.empty:
        raise TypeError("DataFrame can not be empty")
    previous_iter = 0
    while previous_iter < len(df):
        percentage = round(100 * previous_iter / len(df), 2)
        lg.log.info("Generating Insert Queries... %s", percentage)
        batch = df.iloc[previous_iter : previous_iter + batch_size]
        data_points = list(pandas_to_sql(batch))
        data_points_string = ",".join(data_points)
        if schema and table:
            table = f"{schema}.{table}"
        if not table:
            table = "{{table}}"
        sql = f"INSERT INTO {table} VALUES {data_points_string}"
        query = Query(sqlparse.format(sql))
        previous_iter += batch_size
        yield query


def insert_pandas(
    df: pd.DataFrame,
    connection: SQLConnection,
    table: str,
    schema: str,
    batch_size: int,
):
    if not table and schema:
        raise TypeError("Table and Schema need to be provided")
    with Progress() as progress:
        iterations = len(df) / batch_size
        task1 = progress.add_task("[red]Generating Queries...", total=1000)
        task2 = progress.add_task("[green]Inserting Data...", total=iterations)
        task3 = progress.add_task("[cyan]Finishing...", total=1000)
        for i in range(1000):
            progress.update(task1, advance=1.0)
        for query in generate_insert_query(df, table, schema, batch_size):
            connection.execute(query)
            progress.update(task2, advance=1)
        for i in range(1000):
            progress.update(task3, advance=1.0)
