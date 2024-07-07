"""
This module allows to interact with tables in SQL (Create, Alter, etc)
"""

from typing import Any, Union

import pandas as pd
import sqlparse

from pysqltools.src.sql.query import Query

from .constants import TYPE_MAPPING
from .insert import insert_pandas


class Table:
    """
    Class to manipulate SQL Tables
    """

    def __init__(self, table: str, schema: Union[str, None] = None) -> None:
        self.table = table
        if schema:
            self.table = f"{schema}.{table}"

    def create_from_df(
        self,
        df: pd.DataFrame,
        execute: bool = False,
        insert_data: bool = False,
        **insert_kwargs: Any,
    ) -> str:
        """
        Get the SQL statement to create a SQL table based on a Pandas DataFrame. If the insert_data argument is set to True,
        you must pass the same arguments as to the `pysqltools.SQL.insert_pandas` as **kwargs. Example:
        ```python
        table = Table(table = "myTable", schema = "dbo")
        table.create_from_df(df, insert_data = True, connection = myConnection, batch_size = 10000)
        ```
        """
        columns = dict(
            zip(
                df.dtypes.index.to_list(),
                map(
                    lambda x: TYPE_MAPPING[x],
                    map(lambda x: str(x), df.dtypes.to_list()),
                ),
            )
        )
        sql = f"CREATE TABLE IF NOT EXISTS {self.table} ( "
        for k, v in columns.items():
            sql += f"{k} {v}, "
        sql = sql[:-2] + " )"
        if not insert_data:
            return sqlparse.format(sql, encoding="utf-8")
        if execute:
            insert_kwargs["connection"].execute(Query(sql))
        if "batch_size" in insert_kwargs:
            batch_size = insert_kwargs["batch_size"]
        else:
            batch_size = 1000
        try:
            insert_pandas(
                df,
                connection=insert_kwargs["connection"],
                table=self.table,
                batch_size=batch_size,
                dialect=insert_kwargs["dialect"],
            )
        except TypeError as e:
            raise TypeError(
                "Please include the insert arguments into the create_table_from_df method",
                e,
            )
