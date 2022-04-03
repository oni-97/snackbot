import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

app = App(token=os.environ.get("SLACK_BOT_TOKEN"))


@app.message("buy")
def message_buy(message, say):
    # only redpond to DM
    if message["channel_type"] != "im":
        return

    say(
        text="failed to purchase action",
        blocks=[
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "Confirm Purchase\nPrice: *120円*"},
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
    say(f"<@{body['user']['id']}> approved")


@app.action("cancel_buy_action")
def cancel_buy_action(body, ack, say):
    ack()
    say(f"<@{body['user']['id']}> canceled")


if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
