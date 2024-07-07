"""
This module contains all the classes and 
functions to interact with SQL text objects.
"""

import datetime
import os
import re
from typing import Any, Generator, Union

import rich
import rich.progress
import sqlparse
from multimethod import multimethod

from pysqltools.src.log import PabLog, progress_function
from pysqltools.src.sql.exceptions import QueryFormattingError

lg = PabLog("Query")


class QueryException(Exception):
    """
    Exception during Query processing.
    """

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


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
    --------------------------
    ### Parameters
    - sql: property. The string containing the SQL Query
    - parsed: sqlparse object from the SQL Query
    - options: via kwargs. Current options:
        - indent_query (bool) default True: Re-indent the query for output

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

    def __init__(self, sql: str, **kwargs) -> None:
        self._sql = sql.lower()
        self.parsed = sqlparse.parse(sql)[0]
        self.options = kwargs
        self._parameters = None
        self._tables = None
        self._selects = None
        self._windows = None
        self._ctes = None

    @property
    def sql(self):
        """
        Contains the string with the SQL Statement. If the flag `indent_query` has been set on the
        constructor, the sql will be returned with automatic indentation.
        """
        if self.options.get("indent_query", True):
            self._sql = str(
                sqlparse.format(
                    self._sql,
                    keyword_case="lower",
                    id_case="lower",
                    indent_columns=True,
                    reindent=True,
                )
            )
        return self._sql

    @sql.setter
    def sql(self, sql: str):
        self._sql = sql.lower()

    @property
    def ctes(self) -> Generator:
        """
        returns a generator containing all the CTEs on the query. The generator returns
        the CTE identifier as first argument and the CTE Content as second argument.
        """
        cte_regex = re.compile(
            r"""(?i)\b(\w+)\s+as\s+\((.*?)\)(?=\s*,|\s*select|\s*insert|\s*update|\s*delete|\s*with|\Z)""",
            re.DOTALL | re.IGNORECASE | re.MULTILINE,
        )

        matches = cte_regex.findall(self.sql)
        self._ctes = []
        for _, match in enumerate(matches, 1):
            cte_name, cte_content = match
            self._ctes.append((cte_name, cte_content))

        yield from self._ctes

    @ctes.setter
    def ctes(self) -> None:
        raise QueryException("ctes is read-only")

    @property
    def parameters(self) -> Generator:
        """returns a generator containing all the Parameters on the query.
        Parameters must be between {{ }}"""
        regex = re.compile(r"(?<={{)\S*(?=}})")
        self._parameters = regex.findall(self.sql)
        yield from self._parameters

    @parameters.setter
    def parameters(self) -> None:
        raise QueryException("parameters is read-only")

    @property
    def tables(self) -> Generator:
        """Returns a generator containing all the detected tables. CTEs identifiers excluded"""
        regex = re.compile(
            r"(?<=from|join).*?\s*\S*",
            re.DOTALL | re.IGNORECASE | re.MULTILINE,
        )
        self._tables = [r.strip() for r in regex.findall(self.sql)]
        self._tables = [
            t for t in self._tables if t not in [c[0] for c in list(self.ctes)]
        ]
        yield from self._tables

    @tables.setter
    def tables(self, *args: Any) -> None:
        raise QueryException("tables is read-only")

    @property
    def selects(self) -> Generator:
        """returns a generator containing all the Select contents on the query"""
        self._selects = [i.strip() for i in self.__non_greedy_regex("select", "from")]
        yield from self._selects

    @selects.setter
    def selects(self) -> None:
        raise QueryException("selects is read-only")

    @property
    def windows(self) -> Generator:
        """returns a generator containing all the Window Functions on the query"""
        self._windows = [i.strip() for i in self.__non_greedy_regex("over", r"\)")]
        yield from self._windows

    @windows.setter
    def windows(self) -> None:
        raise QueryException("windows is read-only")

    def __non_greedy_regex(self, keyword_start: str, keyword_end: str) -> Generator:
        """"""
        regex = re.compile(
            rf"(?<={keyword_start}).*?(?={keyword_end})",
            re.DOTALL | re.IGNORECASE | re.MULTILINE,
        )
        yield from [i.strip() for i in regex.findall(self.sql)]

    def iter_query_lines(self) -> Generator:
        """
        Iterate the SQL Query line by line.
        """
        yield from self.sql.split("\n")

    def get_ctes_dict(self) -> Generator:
        """
        Get the CTEs on a dictionary

        """
        cte_dict = {}
        for k, v in self.ctes:
            cte_dict.update({k: v})
        return cte_dict

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
        except Exception as e:
            raise QueryFormattingError(e)

        return self

    def get_cte_by_identifier(self, identifier: str) -> Union[None, str]:
        """
        Pass the identifier of one of the query CTEs and get the string containing the content of the CTE.
        """
        if identifier in self.get_ctes_dict():
            return self.get_ctes_dict().get(identifier)
        else:
            return None

    def replace_cte(self, identifier: str, new_cte_content: str) -> "Query":
        """
        Given a CTE identifier, change its content with a new string
        """
        if identifier in self.get_ctes_dict():
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
            "tables": list(self.tables),
            "ctes": self.get_ctes_dict(),
            "parameters": list(self.parameters),
        }


@progress_function("searching queries...", color="green")
def get_queries_from_path(path: str = None, *args, **kwargs) -> list[Query]:
    # lg.add_md("## Scanning Directory for SQL Queries")
    queries = {}
    for dirpath, dirname, filename in os.walk(path):
        lg.log.info(f"Searching {dirpath}...")
        kwargs["progress"].advance(kwargs["task"], 1)
        i = 2
        for f in filename:
            if f.__contains__(".sql"):
                lg.log.info(f"Added item '{f}'")
                if f in queries:
                    name = f.replace(".sql", "") + f"_{i}"
                    i += 1
                else:
                    name = f.replace(".sql", "")
                queries.update(
                    {
                        name: Query(
                            open(os.path.join(dirpath, f), "r", encoding="utf-8").read()
                        )
                    }
                )

    return queries
