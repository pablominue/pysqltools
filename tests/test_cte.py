from src.queries.queries import Query


def test_ctes():
    with open("tests/queries/test_cte.sql", "r", encoding="utf-8") as f:
        sql = f.read()
    q = Query(sql=sql)

    ctes = {cte[0]: cte[1] for cte in q.ctes()}

    assert len(ctes) == 2
