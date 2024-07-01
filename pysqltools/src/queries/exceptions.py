"""
Custom Exception for pysqltools
"""


class QueryFormattingError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


def formatting_method(fun):
    def inner(*args, **kwargs):
        try:
            print(fun(*args, **kwargs))
            return fun(*args, **kwargs)
        except Exception as e:
            raise QueryFormattingError(str(e))

    return inner
