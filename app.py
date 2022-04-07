import json
import os, re
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from database.mysql_util import insert_purchase_data


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

    if is_need_to_pay(price):
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
        say(text=f"*No need* to pay {price}円")


def is_need_to_pay(price):
    # check: price>=unpaid
    return True


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
    if deal_with_pay_action(value["payer_id"], value["price"]):
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
            text=f"*Error* Payment\nPrice: {value['price']}円\nUser:  <@{value['payer_id']}>",
            blocks=list(),
        )

        # update payer message
        admin_user = os.environ.get("SLACK_APP_ADMIN_USER")
        app.client.chat_update(
            channel=value["channel_of_payer"],
            ts=value["ts_of_payer_msg"],
            text=f"`fail to pay: {value['price']}円`\n`contact <@{admin_user}>`",
        )


def deal_with_pay_action(user_id, price):
    price = int(price)
    if price < 0:
        print("Error:", price, "is invalid")
        return False

    # need DB operation
    print(user_id, price)
    return True


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


if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
