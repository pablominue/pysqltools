import os
import sqlite3
from datetime import datetime
from unittest.mock import MagicMock, patch

import mysql
import mysql.connector
import mysql.connector.cursor
import pandas as pd
import pytest

from pysqltools.src.connection.connection import SQLConnection
from pysqltools.src.sql.insert import insert_pandas
from pysqltools.src.sql.query import Query
from pysqltools.src.sql.table import Table

df = pd.DataFrame(
    {
        "id": [1234, 2345, 3456, 4567],
        "dt": [datetime.today() for i in range(4)],
        "description": ["abcd", "cdef", "abcd", "cdef"],
    }
)


@patch("mysql.connector.connection.MySQLConnection.connect")
@patch("mysql.connector.connection.MySQLConnection.cursor")
@patch("mysql.connector.connection.MySQLConnection.commit")
@patch("mysql.connector.cursor.MySQLCursor.execute")
def test_insert_with_conn(mock_connect, mock_cursor, mock_commit, mock_execute):
    mock_connect.return_value = None
    mock_cursor.return_value = mysql.connector.cursor.MySQLCursor()
    mock_commit.return_value = None
    mock_execute.return_value = None
    mock_conn = mysql.connector.connection.MySQLConnection()
    conn = SQLConnection(conn=mock_conn)
    conn.conn.cursor = MagicMock(return_value=mysql.connector.cursor.MySQLCursor())
    try:
        insert_pandas(
            df=df, connection=conn, table="myTable", schema="MySchema", batch_size=1
        )
        result = True
    except:
        result = False
    assert result


@pytest.mark.skip(reason="This test is skipped unconditionally")
def test_sqlite():
    conn = sqlite3.connect("tests/test_db.sqlite3")
    connection = SQLConnection(conn=conn)

    df = pd.DataFrame(
        {
            "id": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            "amount": [
                111342,
                463463,
                6357,
                435765,
                757456,
                84678,
                34,
                7547,
                74567,
                76,
            ],
            "dt": [datetime.today() for _ in range(10)],
            "strings": ["a", "b", "a", "a", "a", "a", "b", "a", "a", "a"],
        }
    )
    table = Table("test_table")
    table.create_from_df(
        df=df,
        execute=True,
        insert_data=True,
        connection=connection,
        batch_size=1,
        dialect="sqlite",
    )

    query = Query("select * from test_table")
    data = connection.fetch(query, dataframe=True)
    os.remove("tests/test_db.sqlite3")
    data["dt"] = pd.to_datetime(data["dt"])
    data = data.iloc[:10]
    df["dt"] = pd.to_datetime(df["dt"])

    assert [df[i].tolist() for i in df.columns] == [
        data[i].tolist() for i in df.columns
    ]
