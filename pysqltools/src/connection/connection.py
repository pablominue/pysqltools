import sqlite3
from typing import Any, Union

import mysql
import mysql.connector
import pandas as pd
import pymssql
import pymysql

# import pyodbc
import sqlalchemy
import trino

from pysqltools.src.connection.exceptions import ConnectionException
from pysqltools.src.log import PabLog
from pysqltools.src.sql.query import Query

lg = PabLog("Connections")


class SQLConnection:
    """
    Unified connection class for different SQL Dialects.
    """

    conn = None

    def __init__(
        self,
        conn: Union[
            pymysql.connections.Connection,
            trino.dbapi.Connection,
            pymssql.Connection,
            sqlite3.Connection,
            # pyodbc.Connection,
            mysql.connector.connection.MySQLConnection,
            mysql.connector.connection_cext.CMySQLConnection,
            ibm_db.IBM_DBConnection,
            sqlalchemy.Connection,
        ],
    ):
        self.conn = conn

    def execute(self, sql: Query) -> None:
        """
        Execute a SQL Statement that returns no value
        """
        try:
            if isinstance(self.conn, sqlalchemy.Connection):
                self.conn.execute(sql.sql)
                self.conn.commit()
            else:
                cursor = self.conn.cursor()
                print(cursor)
                cursor.execute(sql.sql)
                try:
                    self.conn.commit()
                except:
                    lg.log.warning("Connection can not be commited")
        except Exception as e:
            raise ConnectionException(e)

    def fetch(self, sql: Query, dataframe: bool = False):
        """
        Execute a SQL Query object and get the
        """
        try:

            if isinstance(self.conn, sqlalchemy.engine.base.Connection):
                result = self.conn.execute(sql.sql)
                return result.fetchall()

            else:
                cursor = self.conn.cursor()
                cursor.execute(sql.sql)
                if hasattr(cursor, "description"):
                    columns = [i[0] for i in cursor.description]
                if hasattr(cursor, "fetchall"):
                    if dataframe:
                        return pd.DataFrame(cursor.fetchall(), columns=columns)
                    return cursor.fetchall()
                else:
                    rows = []
                    row = cursor.fetchone()
                    while row:
                        rows.append(row)
                        row = cursor.fetchone()
                    if dataframe:
                        return pd.DataFrame(rows)
                    return rows
        except Exception as e:
            lg.log.error(f"Fetch failed: {e}")
            raise ConnectionException
