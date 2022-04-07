from mysql import execute_sql_and_commit, execute_sql_and_fetchall


def insert_purchase_data(user_id, amount):
    try:
        sql = (
            f"insert into purchase_data(user_id, amount)values('{user_id}', '{amount}')"
        )
        execute_sql_and_commit(sql)
        return True
    except Exception as e:
        print(e)
        return False


def insert_payment_data(user_id, amount):
    try:
        sql = (
            f"insert into payment_data(user_id, amount)values('{user_id}', '{amount}')"
        )
        execute_sql_and_commit(sql)
        return True
    except Exception as e:
        print(e)
        return False


def select_purchase_data(user_id):
    try:
        sql = f"SELECT `amount` FROM `purchase_data` WHERE `user_id`='{user_id}'"
        result = execute_sql_and_fetchall(sql)
        return result
    except Exception as e:
        print(e)
        return None


def select_payment_data(user_id):
    try:
        sql = f"SELECT `amount` FROM `payment_data` WHERE `user_id`='{user_id}'"
        result = execute_sql_and_fetchall(sql)
        return result
    except Exception as e:
        print(e)
        return None
