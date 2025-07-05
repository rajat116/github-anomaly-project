# alerts/alerting.py
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import yagmail

# Load from env
SLACK_TOKEN = os.getenv("SLACK_API_TOKEN")
SLACK_CHANNEL = os.getenv("SLACK_CHANNEL", "#general")
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")


# Slack Alert
def send_slack_alert(message: str):
    if not SLACK_TOKEN:
        print("[ALERT] Slack token not configured.")
        return

    client = WebClient(token=SLACK_TOKEN)
    try:
        response = client.chat_postMessage(channel=SLACK_CHANNEL, text=message)
        print(f"[SLACK] Alert sent: {response['message']['text']}")
    except SlackApiError as e:
        print(f"[SLACK ERROR] {e.response['error']}")


# Email Alert
def send_email_alert(subject: str, body: str):
    if not EMAIL_SENDER or not EMAIL_PASSWORD:
        print("[ALERT] Email credentials not configured.")
        return

    try:
        yag = yagmail.SMTP(EMAIL_SENDER, EMAIL_PASSWORD)
        yag.send(to=EMAIL_RECEIVER, subject=subject, contents=body)
        print("[EMAIL] Alert sent successfully.")
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")
