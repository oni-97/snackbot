from database.mysql import execute_sql_and_commit, execute_sql_and_fetchall


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


def insert_payment_data(user_id, amount, table_name, apporover):
    try:
        sql = f"insert into {table_name}(user_id, amount, approver_id)values('{user_id}', '{amount}', '{apporover}')"
        execute_sql_and_commit(sql)
        return True
    except Exception as e:
        print(e)
        return False


def insert_purchase_coffee_data(user_id, amount, item_name):
    try:
        sql = f"insert into purchase_coffee_data(user_id, amount, item_name)values('{user_id}', '{amount}', '{item_name}')"
        execute_sql_and_commit(sql)
        return True
    except Exception as e:
        print(e)
        return False


def select_data(user_id, table_name, limit=None, item="*"):
    try:
        if limit is None:
            sql = f"SELECT {item} FROM {table_name} WHERE user_id='{user_id}'"
        else:
            sql = f"SELECT {item} FROM {table_name} WHERE user_id='{user_id}' ORDER BY id DESC LIMIT {limit}"
        result = execute_sql_and_fetchall(sql)
        return result
    except Exception as e:
        print(e)
        return None
