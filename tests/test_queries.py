from datetime import datetime

import pandas as pd

from pysqltools.src import Query, generate_insert_query


def test_ctes():
    with open("tests/queries/test_cte.sql", "r", encoding="utf-8") as f:
        sql = f.read()
    q = Query(sql=sql)
    ctes = {cte[0]: cte[1] for cte in q.ctes()}

    assert len(ctes) == 2


def test_selects():
    with open("tests/queries/test_cte.sql", "r", encoding="utf-8") as f:
        sql = f.read()
    q = Query(sql=sql)

    selects = {s for s in q.selects()}

    assert len(selects) == 3


def test_windows():
    with open("tests/queries/test_cte.sql", "r", encoding="utf-8") as f:
        sql = f.read()
    q = Query(sql=sql)

    windows = {w for w in q.windows()}
    assert len(windows) == 1


def test_tables():
    with open("tests/queries/test_cte.sql", "r", encoding="utf-8") as f:
        sql = f.read()
    q = Query(sql=sql)

    tables = [t for t in q.tables()]
    assert len(tables) == 5


def test_parameter():
    with open("tests/queries/test_cte.sql", "r", encoding="utf-8") as f:
        sql = f.read()
    q = Query(sql=sql)

    q.format(parameter_table="testschema.xyz")
    assert "testschema.xyz" in q.sql


def test_insert_query():
    df = pd.DataFrame(
        {
            "id": [1234, 2345, 3456, 4567],
            "dt": [datetime.today() for i in range(4)],
            "description": ["abcd", "cdef", "abcd", "cdef"],
        }
    )
    queries = list(generate_insert_query(df=df, table="MyTable", batch_size=2))
    assert len(queries) == 2


def test_cte_replacement():
    with open("tests/queries/test_cte.sql", "r", encoding="utf-8") as f:
        sql = f.read()
    q = Query(sql=sql)
    new_cte = """
        test_2_cte as (
        select 
            new_cte_value,
            count(*) over (partition by id order by dt desc) as id_total

        from {{parameter_table}} c
        )
        """
    q.replace_cte("test_2_cte", new_cte_content=new_cte)
    assert new_cte in q.sql
