import logging
from queue import Queue
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

log = logging.getLogger(__name__)


class SomeSlackBot:
    def __init__(self, bot_token: str, app_token: str, signing_key: str, message_queue: Queue):
        self.message_queue = message_queue
        self.app = App(token=bot_token, signing_secret=signing_key)
        self.handler = SocketModeHandler(self.app, app_token)
        self.client = WebClient(token=bot_token)
        self.uid2name = {}
        self.cid2name = {}

        self.app.message()(self.handle_message_events)

    def run(self):
        # self.fetch_user_id_to_username_mapping()
        self.fetch_channel_id_to_name_mapping()
        self.handler.start()

    def fetch_user_id_to_username_mapping(self):
        try:
            for response in self.client.users_list(limit=200):
                users = response["members"]
                for user in users:
                    if "name" in user and "id" in user:
                        self.uid2name[user["id"]] = user["name"]
        except SlackApiError as e:
            print(f"Error fetching users list: {e}")

    def fetch_channel_id_to_name_mapping(self):
        print("Fetching channel list")
        try:
            for response in self.client.conversations_list(limit=200, types="public_channel,private_channel"):
                channels = response["channels"]
                for channel in channels:
                    if channel.get("name") and channel.get("id") and channel.get("is_channel"):
                        print(f"Adding channel {channel['name']} with id {channel['id']} to mapping")
                        self.cid2name[channel["id"]] = channel["name"]
        except SlackApiError as e:
            print(f"Error fetching channels list: {e}")

    def handle_message_events(self, event, say):
        if event.get("type") == "message" and event.get("subtype") == "bot_message":
            log.debug("Got message in Slack, sending to queue")
            channel_id = event.get("channel")
            channel_name = self.cid2name.get(channel_id)
            event["channel_name"] = channel_name
            self.message_queue.put(event)
