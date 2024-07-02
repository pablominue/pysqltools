import sqlite3
from typing import Any, Union

import ibm_db
import mysql
import mysql.connector
import pymssql
import pymysql

# import pyodbc
import sqlalchemy
import trino

from pysqltools.src.connection.exceptions import ConnectionException
from pysqltools.src.log import PabLog
from pysqltools.src.queries.query import Query

lg = PabLog("Connections")


class SQLConnection:
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
        try:
            if isinstance(self.conn, ibm_db.IBM_DBConnection):
                ibm_db.exec_immediate(self.conn, sql.sql)
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
        except:
            raise ConnectionException

    def fetch(self, sql: Query):
        try:
            if isinstance(self.conn, ibm_db.IBM_DBConnection):
                stmt = ibm_db.exec_immediate(self.conn, sql.sql)
                rows = []
                row = ibm_db.fetch_assoc(stmt)
                while row:
                    rows.append(row)
                    row = ibm_db.fetch_assoc(stmt)
                return rows

            if isinstance(self.conn, sqlalchemy.engine.base.Connection):
                result = self.conn.execute(sql.sql)
                return result.fetchall()

            else:
                cursor = self.conn.cursor()
                cursor.execute(sql.sql)
                if hasattr(cursor, "fetchall"):
                    return cursor.fetchall()
                else:
                    rows = []
                    row = cursor.fetchone()
                    while row:
                        rows.append(row)
                        row = cursor.fetchone()
                    return rows
        except Exception as e:
            lg.log.error(f"Fetch failed: {e}")
            raise ConnectionException
