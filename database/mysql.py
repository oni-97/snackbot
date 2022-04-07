import os
import pymysql.cursors, pymysql


connection = pymysql.connect(
    host="localhost",
    user=os.environ["MYSQL_USER"],
    password=os.environ["MYSQL_USER_PASS"],
    database=os.environ["MYSQL_DB_NAME"],
    cursorclass=pymysql.cursors.DictCursor,
)


def execute_sql_and_commit(sql):
    # before execute, check if the server is alive
    # If the connection is closed, reconnect
    connection.ping(reconnect=True)
    with connection.cursor() as cursor:
        cursor.execute(sql)

    connection.commit()


def execute_sql_and_fetchall(sql):
    # before execute, check if the server is alive
    # If the connection is closed, reconnect
    connection.ping(reconnect=True)
    with connection.cursor() as cursor:
        cursor.execute(sql)
        result = cursor.fetchall()
        return result
