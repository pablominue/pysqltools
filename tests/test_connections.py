from datetime import datetime
from unittest.mock import MagicMock, patch

import mysql
import mysql.connector
import mysql.connector.cursor
import pandas as pd

from pysqltools.src.connection.connection import SQLConnection
from pysqltools.src.SQL.insert import insert_pandas

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
        insert_pandas(df, conn, "myTable", "MySchema", batch_size=1)
        result = True
    except:
        result = False
    assert result
