from mysql import execute_sql


try:
    sql = "insert into purchase_data(user_id, amount)values('age23', 35)"
    execute_sql(sql)
    sql = "insert into purchase_data(user_id, amount)values('dge24', -187)"
    execute_sql(sql)
except Exception as e:
    print(e)
