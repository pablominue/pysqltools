"""
This module allows to interact with tables in SQL (Create, Alter, etc)
"""

from typing import Any, Union

import pandas as pd
import sqlparse

from .constants import TYPE_MAPPING


class Table:
    def __init__(self, table: str, schema: Union[str, None] = None) -> None:
        self.table = table
        if schema:
            self.table = f"{schema}.{table}"

    def create_from_df(self, df: pd.DataFrame) -> str:
        columns = dict(
            zip(
                df.dtypes.index.to_list(),
                map(
                    lambda x: TYPE_MAPPING[x],
                    map(lambda x: str(x), df.dtypes.to_list()),
                ),
            )
        )
        sql = f"CREATE TABLE {self.table} ( "
        for k, v in columns.items():
            sql += f"{k} {v}, "
        sql = sql[:-2] + " )"
        return sqlparse.format(sql, encoding="utf-8")
