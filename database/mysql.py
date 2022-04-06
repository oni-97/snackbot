import os
import pymysql.cursors, pymysql


class MySQL:
    def __init__(self, database):
        self.__connection = pymysql.connect(
            host="localhost",
            user=os.environ["MYSQL_USER"],
            password=os.environ["MYSQL_USER_PASS"],
            database=os.environ["MYSQL_DB_NAME"],
            cursorclass=pymysql.cursors.DictCursor,
        )

    @property
    def connection(self):
        return self.__connection

    def executal(self, sql):
        # before execute, check if the server is alive
        # If the connection is closed, reconnect
        self.connection.ping(reconnect=True)
        with self.connection.cursor() as cursor:
            cursor.execute(sql)

        self.connection.commit()
