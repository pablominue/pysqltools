from pysqltools import Query

q = Query("""
select
    a,
    b,
    c
from 
    mychema.ttable
    where c in (select * from my.othertable)
""")

for i in q.selects:
    print('select')
    print(i)