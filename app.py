import os, re
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

app = App(token=os.environ.get("SLACK_BOT_TOKEN"))


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
                    "text": "Confirm Purchase\nPrice: *" + price + "円*",
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
def approve_buy_action(body, ack, say):
    ack()
    user_id = body["user"]["id"]
    price = extract_price_from_body(body)
    if add_purchase_data_to_db(user_id, price):
        say(f"<@{body['user']['id']}> approved")


def extract_price_from_body(body):
    text = body["message"]["blocks"][0]["text"]["text"]
    pattern = re.compile("^Confirm\sPurchase\\nPrice:\s\*(\d+)円\*$")
    if pattern.match(text):
        price_str = text.replace("Confirm Purchase\nPrice: *", "").replace("円*", "")
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
def cancel_buy_action(body, ack, say):
    ack()
    say(f"<@{body['user']['id']}> canceled")


if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
