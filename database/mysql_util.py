from database.mysql import execute_sql


def insert_purchase_data(user_id, amount):
    try:
        sql = (
            f"insert into purchase_data(user_id, amount)values('{user_id}', '{amount}')"
        )
        execute_sql(sql)
        return True
    except Exception as e:
        print(e)
        return False


def insert_payment_data(user_id, amount):
    try:
        sql = (
            f"insert into payment_data(user_id, amount)values('{user_id}', '{amount}')"
        )
        execute_sql(sql)
        return True
    except Exception as e:
        print(e)
        return False
