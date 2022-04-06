from mysql import MySQL


try:
    mysql = MySQL("snackbot_db")
    sql = "insert into purchase_data(user_id, amount)values('age23', 76431)"
    mysql.executal(sql)
    sql = "insert into purchase_data(user_id, amount)values('dge24', -187)"
    mysql.executal(sql)
except Exception as e:
    print(e)
