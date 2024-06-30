import datetime
import re
from typing import Generator

from multimethod import multimethod


class SQLStatement(str):
    pass


class Query:
    def __init__(self, sql: str) -> None:
        self.sql = sql.lower()

    def ctes(self) -> Generator:
        cte_regex = re.compile(
            r"(?i)\b(\w+)\s+as\s+\((.*?)\)(?=\s*,|\s*select|\s*insert|\s*update|\s*delete|\s*with|\Z)",
            re.DOTALL | re.IGNORECASE,
        )

        matches = cte_regex.findall(self.sql)

        for i, match in enumerate(matches, 1):
            cte_name, cte_content = match
            yield (cte_name, CTE(cte_content))

    def parameters(self) -> Generator:
        regex = re.compile(r"(?<={{)\S*(?=}})")
        parameters = regex.findall(self.sql)
        for p in parameters:
            yield p

    def __non_greedy_regex(self, keyword_start: str, keyword_end: str) -> Generator:
        regex = re.compile(fr"(?<={keyword_start}).*?(?={keyword_end})", re.DOTALL | re.IGNORECASE)
        items = regex.findall(self.sql)
        for i in items:
            yield i

    def selects(self) -> Generator:
        return self.__non_greedy_regex("select","from")
    
    def froms(self) -> Generator:
        return self.__non_greedy_regex("select","from")

    def format(self, **kwargs) -> str:
        for k, v in kwargs.items():
            self.sql = self.sql.replace("{{" + k + "}}", assign_parameter(v))
        return self.sql

    def __str__(self):
        return self.sql


class SQLString(str):
    pass


class CTE(Query):
    def __init__(self, sql: str) -> None:
        super().__init__(sql)


@multimethod
def assign_parameter(param: str) -> str:
    return "'" + param + "'"


@multimethod
def assign_parameter(param: int) -> str:
    return param


@multimethod
def assign_parameter(param: SQLString) -> str:
    return param


@multimethod
def assign_parameter(param: list[str]) -> str:
    string = "("
    for item in param:
        string += f"'{item}', "
    return string[:-2] + ")"


@multimethod
def assign_parameter(param: list[int]) -> str:
    string = "("
    for item in param:
        string += f"{item}, "
    return string[:-2] + ")"


@multimethod
def assign_parameter(param: datetime.datetime) -> str:
    return "datetime '" + param.strftime("%Y-%m-%d %H:%M:%S") + "'"
