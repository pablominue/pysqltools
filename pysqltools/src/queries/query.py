"""
This module contains all the classes and 
functions to interact with SQL text objects.
"""

import datetime
import re
from typing import Generator, Union

import sqlparse
from multimethod import multimethod

from pysqltools.src.queries.exceptions import QueryFormattingError


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
    ### Query Module
    The query module provides a Query class to work with Query objects, which will allow to modify the
    SQL Queries on an easy way with the class methods, and easily access the sql string with the sql
    attribute of the objects.

    To add parameters to the query, use {{parameter}} on the SQL String.

    The current methods are:

    - ctes: Generator that yields the CTEs of the Query
    - selects: Generator that yields the Select statements of the Query
    - Windows: Generator that yields the Window Function contents of the query
    - tables: Generator that yields the detected tables on the query
    - parameters: Generator that yields all the parameters on the Query
    - format: allows to assign values to the parameters in the query. Current supported types are str, int, float, datetime.datetime, list[int, float, str]
    To call the format function, just call the parameters you have defined on your query. Example:
    query:
    `select * from {{table_param}} limit 20`

    function call:
    `query = Query(sql = sql).format(table_param = "MyTable")`
    """

    def __init__(self, sql: str) -> None:
        self.sql = sql.lower()
        self.parsed = sqlparse.parse(sql)[0]

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
        yield from [i.strip() for i in regex.findall(self.sql)]

    def selects(self) -> Generator:
        """returns a generator containing all the Select contents on the query"""
        yield from [i.strip() for i in self.__non_greedy_regex("select", "from")]

    def windows(self) -> Generator:
        """returns a generator containing all the Window Functions on the query"""
        yield from [i.strip() for i in self.__non_greedy_regex("over", r"\)")]

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
        you can substitute the parameters with python variables.\n
        An special type SQLString is used for tables, as we don't want to include "'" on
        those strings.\n

        `sql = Query(sql="select * from {{my_table}} where country in {{country_list}}")` \n
        `sql.format(my_table=SQLString("schema.table"), country_list = ['ES', 'GB'])`
        """
        try:
            for k, v in kwargs.items():
                self.sql = self.sql.replace("{{" + k + "}}", assign_parameter(v))
            self.parsed = sqlparse.parse(sql=self.sql)[0]
        except:
            raise QueryFormattingError

        return self

    def get_cte_by_identifier(self, identifier: str) -> Union[None, str]:
        """
        Pass the identifier of one of the query CTEs and get the string containing the content of the CTE.
        """
        ctes = {i: c for i, c in self.ctes()}
        if identifier in ctes:
            return ctes.get(identifier)
        else:
            return None

    def replace_cte(self, identifier: str, new_cte_content: str) -> "Query":
        """
        Given a CTE identifier, change its content with a new string
        """
        ctes = {i: c for i, c in self.ctes()}
        if identifier in ctes:
            self.sql = self.sql.replace(
                self.get_cte_by_identifier(identifier), new_cte_content
            )
            return self
        else:
            raise TypeError(f"CTE with dentifier {identifier} not found in Query")

    def __str__(self):
        return self.sql

    def __dict__(self):
        return {
            "tables": list(self.tables()),
            "ctes": list(self.ctes),
            "parameters": list(self.parameters()),
        }
