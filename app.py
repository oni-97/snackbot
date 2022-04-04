import os, re
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

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
                    "text": f"Confirm Purchase\nPrice: *{price}円*",
                },
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Buy", "emoji": True},
                        "style": "primary",
                        "action_id": "approve_buy_action",
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Cancel", "emoji": True},
                        "style": "danger",
                        "action_id": "cancel_buy_action",
                    },
                ],
            },
        ],
    )


@app.action("approve_buy_action")
def approve_buy_action(body, ack):
    # Acknowledge the action
    ack()

    price = extract_price_from_body(body)
    # button pushed, update message
    result = app.client.chat_update(
        channel=body["channel"]["id"],
        ts=body["message"]["ts"],
        text=f"purchasing...",
        blocks=list(),
    )

    # insert data into DB and update message responding to the result
    user_id = body["user"]["id"]
    if add_purchase_data_to_db(user_id, price):
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


def extract_price_from_body(body):
    text = body["message"]["blocks"][0]["text"]["text"]
    pattern = re.compile("^Confirm\sPurchase\\nPrice:\s\*([1-9][0-9]*)円\*$")
    if pattern.match(text):
        price_str = re.search(r"([1-9][0-9]*)", text).group()
        return int(price_str)
    else:
        return 0


def add_purchase_data_to_db(user_id, price):
    if price < 0:
        print("Error:", price, "is invalid")
        return False

    # need DB operation
    print(user_id, price)
    return True


@app.action("cancel_buy_action")
def cancel_buy_action(body, ack):
    # Acknowledge the action
    ack()

    price = extract_price_from_body(body)
    # button pushed, update message
    result = app.client.chat_update(
        channel=body["channel"]["id"],
        ts=body["message"]["ts"],
        text=f"*canceled* purchase: {price}円",
        blocks=list(),
    )


if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
