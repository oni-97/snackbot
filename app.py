import datetime
import json
import os, re
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from database.calculator import unpaid_amount

from database.mysql_util import (
    insert_coffee_or_tea_data,
    insert_payment_data,
    insert_purchase_data,
    select_data,
)


app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# listenig and responding to "buy <natural number>"
@app.message(re.compile("^(\s*)(buy)(\s+)([1-9][0-9]*)(\s*)$"))
def message_buy(message, say):
    # only redpond to DM
    if message["channel_type"] != "im":
        return

    price = message["text"].split()[1]

    say(
        text="failed to purchase action",
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Confirm Purchase\n• Price: *{price}円*",
                },
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Buy", "emoji": True},
                        "style": "primary",
                        "value": price,
                        "action_id": "take_buy_action",
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Cancel", "emoji": True},
                        "style": "danger",
                        "value": price,
                        "action_id": "cancel_buy_action",
                    },
                ],
            },
        ],
    )


@app.action("take_buy_action")
def take_buy_action(payload, body, ack):
    # Acknowledge the action
    ack()

    price = int(payload["value"])
    # button pushed, update message
    result = app.client.chat_update(
        channel=body["channel"]["id"],
        ts=body["message"]["ts"],
        text=f"purchasing...",
        blocks=list(),
    )

    # insert data into DB and update message responding to the result
    user_id = body["user"]["id"]
    if insert_purchase_data(user_id, price):
        app.client.chat_update(
            channel=result["channel"],
            ts=result["ts"],
            text=f"*success* to purchase: {price}円",
        )
    else:
        admin_user = os.environ.get("SLACK_APP_ADMIN_USER")
        app.client.chat_update(
            channel=result["channel"],
            ts=result["ts"],
            text=f"`fail to purchase: {price}円`\n`contact <@{admin_user}>`",
        )


@app.action("cancel_buy_action")
def cancel_buy_action(payload, body, ack):
    # Acknowledge the action
    ack()

    price = int(payload["value"])
    # button pushed, update message
    app.client.chat_update(
        channel=body["channel"]["id"],
        ts=body["message"]["ts"],
        text=f"*canceled* purchase: {price}円",
        blocks=list(),
    )


# listenig and responding to "pay <natural number>"
@app.message(re.compile("^(\s*)(pay)(\s+)([1-9][0-9]*)(\s*)$"))
def message_pay(message, say):
    # only redpond to DM
    if message["channel_type"] != "im":
        return

    price = message["text"].split()[1]
    flag, unpaid = is_need_to_pay(int(price), message["user"])
    if flag is None:
        admin_user = os.environ.get("SLACK_APP_ADMIN_USER")
        say(text=f"`fail to pay: {price}円`\n`contact <@{admin_user}>`"),
    elif flag:
        say(
            text="failed to purchase action",
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"Confirm Payment\n• Price: *{price}円*",
                    },
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Pay",
                                "emoji": True,
                            },
                            "style": "primary",
                            "value": price,
                            "action_id": "take_pay_action",
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Cancel",
                                "emoji": True,
                            },
                            "style": "danger",
                            "value": price,
                            "action_id": "cancel_pay_action",
                        },
                    ],
                },
            ],
        )
    else:
        say(text=f"*No need* to pay {price}円\nyour unpaid amount: *{unpaid}円*")


def is_need_to_pay(price, user_id):
    # check: unpaid>=unpaid
    unpaid = unpaid_amount(user_id)
    if unpaid is None:
        return None, 0

    if unpaid >= price:
        return True, unpaid
    else:
        return False, unpaid


@app.action("cancel_pay_action")
def cancel_pay_action(payload, body, ack):
    # Acknowledge the action
    ack()

    price = payload["value"]
    # cancel button pushed, update message
    app.client.chat_update(
        channel=body["channel"]["id"],
        ts=body["message"]["ts"],
        text=f"*canceled* payment: {price}円",
        blocks=list(),
    )


@app.action("take_pay_action")
def take_pay_action(payload, body, ack, say):
    # Acknowledge the action
    ack()

    price = payload["value"]
    # pay button pushed, update message
    result = app.client.chat_update(
        channel=body["channel"]["id"],
        ts=body["message"]["ts"],
        text=f"paying {price}円 ...",
        blocks=list(),
    )

    # post message of payment approve to admin channel
    user_id = body["user"]["id"]
    button_value = json.dumps(
        {
            "price": price,
            "payer_id": user_id,
            "ts_of_payer_msg": result["ts"],
            "channel_of_payer": result["channel"],
        }
    )
    say(
        channel=os.environ.get("SLACK_APP_ADMIN_CHANNEL"),
        text="approve payment",
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Payment request\n• Price: *{price}円*\n• User: *<@{user_id}>*",
                },
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Approve",
                            "emoji": True,
                        },
                        "style": "primary",
                        "value": button_value,
                        "action_id": "approve_pay_action",
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Reject",
                            "emoji": True,
                        },
                        "style": "danger",
                        "value": button_value,
                        "action_id": "reject_pay_action",
                    },
                ],
            },
        ],
    )


@app.action("approve_pay_action")
def approve_pay_action(payload, body, ack):
    # Acknowledge the action
    ack()

    value = json.loads(payload["value"])
    # approve button pushed, perform DB operation
    if insert_payment_data(value["payer_id"], value["price"]):
        # update admin message
        action_user = body["user"]["id"]
        app.client.chat_update(
            channel=body["channel"]["id"],
            ts=body["message"]["ts"],
            text=f"*<@{action_user}> approved* payment\n• Price: {value['price']}円\n• User:  <@{value['payer_id']}>",
            blocks=list(),
        )

        # update payer message
        app.client.chat_update(
            channel=value["channel_of_payer"],
            ts=value["ts_of_payer_msg"],
            text=f"*success* to pay: {value['price']}円",
            blocks=list(),
        )
    else:
        # update admin message
        app.client.chat_update(
            channel=body["channel"]["id"],
            ts=body["message"]["ts"],
            text=f"`Error Payment`\nPrice: {value['price']}円\nUser:  <@{value['payer_id']}>",
            blocks=list(),
        )

        # update payer message
        admin_user = os.environ.get("SLACK_APP_ADMIN_USER")
        app.client.chat_update(
            channel=value["channel_of_payer"],
            ts=value["ts_of_payer_msg"],
            text=f"`fail to pay: {value['price']}円`\n`contact <@{admin_user}>`",
        )


@app.action("reject_pay_action")
def reject_pay_action(payload, body, ack):
    # Acknowledge the action
    ack()

    action_user = body["user"]["id"]
    value = json.loads(payload["value"])
    # reject button pushed, update admin message
    app.client.chat_update(
        channel=body["channel"]["id"],
        ts=body["message"]["ts"],
        text=f"*<@{action_user}> rejected* payment\n• Price: {value['price']}円\n• User:  <@{value['payer_id']}>",
        blocks=list(),
    )

    # reject button pushed, update payer message
    app.client.chat_update(
        channel=value["channel_of_payer"],
        ts=value["ts_of_payer_msg"],
        text=f"payment *rejected*: {value['price']}円",
        blocks=list(),
    )


# listenig and responding to "unpaid"
@app.message(re.compile("^(\s*)(unpaid)(\s*)$"))
def message_buy(message, say):
    # only redpond to DM
    if message["channel_type"] != "im":
        return

    # return unpaid amount to user
    unpaid = unpaid_amount(user_id=message["user"])
    if unpaid is None:
        admin_user = os.environ.get("SLACK_APP_ADMIN_USER")
        say(text=f"`fail to unpaid`\n`contact <@{admin_user}>`")
    else:
        say(text=f"unpaid: *{unpaid}円*")


# listenig and responding to "history"
@app.message(re.compile("^(\s*)(history)(\s+)(buy|pay)(\s*|\s+[1-9])$"))
def message_buy(message, say):
    # only redpond to DM
    if message["channel_type"] != "im":
        return

    args = message["text"].split()

    # set maximum display number
    if len(args) > 2:
        limit = int(args[2])
    else:
        limit = 9

    # set table name depending on arg
    pay_or_buy = args[1]
    if pay_or_buy == "pay":
        table_name = "payment_data"
    else:
        table_name = "purchase_data"

    data_list = select_data(user_id=message["user"], table_name=table_name, limit=limit)
    if data_list is None:
        admin_user = os.environ.get("SLACK_APP_ADMIN_USER")
        say(text=f"`fail to history`\n`contact <@{admin_user}>`")
    elif len(data_list) == 0:
        say(text=f"No {args[1]} history")
    else:
        text = f"History {args[1]}"
        index = 1
        for data in data_list:
            date = data["created_at"].strftime("%Y年%m月%d日 %H時%M分%S秒")
            text += f"\n{index}.  {date} : {data['amount']}円"
            index += 1
        say(text=text)


# listenig and responding to "coffee" or "tea"
@app.message(re.compile("^(\s*)(coffee|tea)(\s*)$"))
def message_coffee_or_tea(message, say):
    # only redpond to DM
    if message["channel_type"] != "im":
        return

    coffee_or_tea = message["text"].replace(" ", "")
    if coffee_or_tea == "coffee":
        price = 20
    elif coffee_or_tea == "tea":
        price = 20
    else:
        price = 0

    value = json.dumps(
        {
            "price": price,
            "item_name": coffee_or_tea,
        }
    )

    say(
        text="you are not suppprted",
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Confirm Purchase\n• {coffee_or_tea}: *{price}円*",
                },
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Buy", "emoji": True},
                        "style": "primary",
                        "value": value,
                        "action_id": "take_coffee_or_tea_action",
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Cancel", "emoji": True},
                        "style": "danger",
                        "value": value,
                        "action_id": "cancel_coffee_or_tea_action",
                    },
                ],
            },
        ],
    )


@app.action("take_coffee_or_tea_action")
def take_coffee_or_tea_action(payload, body, ack):
    # Acknowledge the action
    ack()

    value = json.loads(payload["value"])
    # buy button pushed, update message
    result = app.client.chat_update(
        channel=body["channel"]["id"],
        ts=body["message"]["ts"],
        text=f"purchasing...",
        blocks=list(),
    )

    # insert data into DB and update message responding to the result
    user_id = body["user"]["id"]
    if insert_coffee_or_tea_data(user_id, int(value["price"]), value["item_name"]):
        app.client.chat_update(
            channel=result["channel"],
            ts=result["ts"],
            text=f"*success* to {value['item_name']}: {value['price']}円",
        )
    else:
        admin_user = os.environ.get("SLACK_APP_ADMIN_USER")
        app.client.chat_update(
            channel=result["channel"],
            ts=result["ts"],
            text=f"`fail to {value['item_name']}: {value['price']}円`\n`contact <@{admin_user}>`",
        )


@app.action("cancel_coffee_or_tea_action")
def cancel_coffee_or_tea_action(payload, body, ack):
    # Acknowledge the action
    ack()

    value = json.loads(payload["value"])
    # cancel button pushed, update message
    app.client.chat_update(
        channel=body["channel"]["id"],
        ts=body["message"]["ts"],
        text=f"*canceled* {value['item_name']}: {value['price']}円",
        blocks=list(),
    )


if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
