from database.mysql_util import select_data


def total_amount_of_payment(user_id):
    return caluculate_total_amount(user_id=user_id, table_name="payment_data")


def total_amount_of_purchase(user_id):
    return caluculate_total_amount(user_id=user_id, table_name="purchase_data")


def total_amount_of_coffee_payment(user_id):
    return caluculate_total_amount(user_id=user_id, table_name=" payment_coffee_data")


def total_amount_of_coffee_purchase(user_id):
    return caluculate_total_amount(user_id=user_id, table_name="purchase_coffee_data")


def caluculate_total_amount(user_id, table_name):
    data_list = select_data(user_id=user_id, table_name=table_name)
    if data_list is None:
        return None

    total = 0
    for data in data_list:
        total += data["amount"]
    return total


def unpaid_amount(user_id):
    payment_amount = total_amount_of_payment(user_id=user_id)
    purchase_amount = total_amount_of_purchase(user_id=user_id)
    payment_coffee_amount = total_amount_of_coffee_payment(user_id=user_id)
    purchase_coffee_amount = total_amount_of_coffee_purchase(user_id=user_id)
    if (
        (payment_amount is None)
        or (purchase_amount is None)
        or (payment_coffee_amount is None)
        or (purchase_coffee_amount is None)
    ):
        return None

    return (
        purchase_amount - payment_amount,
        purchase_coffee_amount - payment_coffee_amount,
    )
