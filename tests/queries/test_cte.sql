with test_1_cte as (
    select
        a.id,
        b.dt,
        sum(b.amount)
    from
        table1 a
            inner join
                table2 b
                    on a.id = b.user_id
    where
        b.amount > 2000
    group by 1,2
),

test_2_cte as (
    select 
        *,
        count(*) over (partition by id order by dt desc) as id_total

    from table3 c
)

select
    x.id,
    x.dt,
    y.id_total
from 
    test_1_cte x
    join
        test_2_cte y
        on x.id = y.id
        
