from pysqltools.src import Query


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
