"""
This module contains all the classes and 
functions to interact with SQL text objects.
"""

import datetime
import re
from typing import Generator, Union

from multimethod import multimethod


class SQLString(str):
    """
    String Class used to format queries without adding single quotes.
    """


@multimethod
def assign_parameter(param: str) -> str:
    """
    assign parameter function
    """
    return "'" + param + "'"


@multimethod
def assign_parameter(param: Union[int, float]) -> str:
    """
    assign parameter function
    """
    return param


@multimethod
def assign_parameter(param: SQLString) -> str:
    """
    assign parameter function
    """
    return param


@multimethod
def assign_parameter(param: list[str]) -> str:
    """
    assign parameter function
    """
    string = "("
    for item in param:
        string += f"'{item}', "
    return string[:-2] + ")"


@multimethod
def assign_parameter(param: list[int, float]) -> str:
    """
    assign parameter function
    """
    string = "("
    for item in param:
        string += f"{item}, "
    return string[:-2] + ")"


@multimethod
def assign_parameter(param: datetime.datetime) -> str:
    """
    assign parameter function
    """
    return "datetime '" + param.strftime("%Y-%m-%d %H:%M:%S") + "'"


class Query:
    """
    ## Class Query:
    ### Description
    The query class allows you to instantiate a SQL Query string to perform different methods,
     collect ctes, statements, etc

    ### Attributes
    - sql: Contains the SQL Query text

    ### Methods:
    - ctes: returns a generator containing all the CTEs on the query
    - selects: returns a generator containing all the select contents of the query
    - windows: returns a generator containing all the window functions of the query
    """

    def __init__(self, sql: str) -> None:
        self.sql = sql.lower()

    def ctes(self) -> Generator:
        """
        returns a generator containing all the CTEs on the query
        """
        cte_regex = re.compile(
            r"""(?i)\b(\w+)\s+as\s+\((.*?)\)(?=\s*,|\s*select|\s*insert|\s*update|\s*delete|\s*with|\Z)""",
            re.DOTALL | re.IGNORECASE | re.MULTILINE,
        )

        matches = cte_regex.findall(self.sql)

        for _, match in enumerate(matches, 1):
            cte_name, cte_content = match
            yield (cte_name, cte_content)

    def parameters(self) -> Generator:
        """returns a generator containing all the Parameters on the query.
        Parameters must be between {{ }}"""
        regex = re.compile(r"(?<={{)\S*(?=}})")
        yield from regex.findall(self.sql)

    def __non_greedy_regex(self, keyword_start: str, keyword_end: str) -> Generator:
        """"""
        regex = re.compile(
            rf"(?<={keyword_start}).*?(?={keyword_end})",
            re.DOTALL | re.IGNORECASE | re.MULTILINE,
        )
        yield from regex.findall(self.sql)

    def selects(self) -> Generator:
        """returns a generator containing all the Select contents on the query"""
        yield from self.__non_greedy_regex("select", "from")

    def windows(self) -> Generator:
        """returns a generator containing all the Window Functions on the query"""
        yield from self.__non_greedy_regex("over", r"\)")

    def tables(self) -> Generator:
        """Returns a generator containing all the detected tables"""
        regex = re.compile(
            r"(?<=from|join).*?\s*\S*",
            re.DOTALL | re.IGNORECASE | re.MULTILINE,
        )
        results = regex.findall(self.sql)
        results = [r.strip() for r in results]
        yield from results

    def format(self, **kwargs) -> "Query":
        """
        Allows dynamic variables on SQL Queries.
        The parameters must be between keys i.e. {{parameter}}. Using the format function,
        you can substitute the parameters with python variables.
        An special type SQLString is used for tables, as we don't want to include "'" on
        those strings.

        sql = Query(sql="select * from {{my_table}} where country in {{country_list}}")
        sql.format(my_table=SQLString("schema.table"), country_list = ['ES', 'GB'])
        """
        for k, v in kwargs.items():
            self.sql = self.sql.replace("{{" + k + "}}", assign_parameter(v))

        return self

    def __str__(self):
        return self.sql

    def __dict__(self):
        return {
            "tables": list(self.tables()),
            "ctes": list(self.ctes),
            "parameters": list(self.parameters()),
        }
