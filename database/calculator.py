from database.mysql_util import select_payment_data, select_purchase_data


def total_amount_of_payment(user_id):
    pay_data = select_payment_data(user_id)
    total = 0
    for data in pay_data:
        total += data["amount"]
    return total


def total_amount_of_purchase(user_id):
    pay_data = select_purchase_data(user_id)
    total = 0
    for data in pay_data:
        total += data["amount"]
    return total


def unpaid_amount(user_id):
    payment_amount = total_amount_of_payment(user_id=user_id)
    purchase_amount = total_amount_of_purchase(user_id=user_id)
    return purchase_amount - payment_amount
