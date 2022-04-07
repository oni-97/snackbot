import os
from mysql import execute_sql_and_commit
from mysql_util import select_payment_data, select_purchase_data


def insert_test():
    try:
        sql = "insert into purchase_data(user_id, amount)values('age23', 35)"
        execute_sql_and_commit(sql)
        sql = "insert into purchase_data(user_id, amount)values('dge24', -187)"
        execute_sql_and_commit(sql)
    except Exception as e:
        print(e)


def select_test():
    print(select_purchase_data(os.environ.get("SLACK_APP_ADMIN_USER")))
    print(select_payment_data(os.environ.get("SLACK_APP_ADMIN_USER")))


select_test()
