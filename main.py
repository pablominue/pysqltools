from pysqltools import Query

with open("tests/queries/test_cte.sql", "r", encoding="utf-8") as f:
    sql = f.read()
q = Query(sql=sql)

for select in q.selects():
    print(select)