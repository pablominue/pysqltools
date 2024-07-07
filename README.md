# pysqltools

PySQLTools tries to ease the interaction between Python and SQL. The idea behind this project is
to provide an easy framework to manage the interaction between this two languages. It allows dynamic
queries management, using parameters in the SQL queries that can be later easily manipulated with
the provided tools.

## Install
you can install the latest distribution by 
`pip install pysqltools`

## Current Features

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

### Insert Module

More to be developed. For now, it contains a Generator `generate_insert_query` twith the following inputs:
- df: pd.DataFrame containing the data we want to insert
- table: name of the table we want to insert into
- schema: name of the schema were the table is located
- batch_size: How many rows on one insert query
Note: if no table is provided, a parameter {{table}} will be automatically created on the Query object. It can be later changed using the .format() method.


The Generator yields Insert Queries (with `batch_size` rows) that can be iterated to execute.

### Connection Module

Allows to instantiate a SQL Connection to execute and fetch results (i.e., use the insert_pandas method from the insert module) Supported connections:

- ibm_db
- mysql
- pymssql
- pymysql
- sqlalchemy
- trino

### Table Module

Allows to create tables on a SQL Database given a pandas DataFrame. Also contains the option to insert the data of the dataframe in the 
new table by calling the insert module