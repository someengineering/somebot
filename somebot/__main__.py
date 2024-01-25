#!/usr/bin/env python
# Copyright 2022 Some Engineering Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os
import sys
import logging
import threading
import signal
import queue
from .discord_bot import SomeDiscordBot
from .slack_bot import SomeSlackBot
from typing import Any


log_format = "%(asctime)s - %(levelname)s - %(threadName)s - %(message)s"
logging.basicConfig(level=logging.WARN, format=log_format)
logging.getLogger("somebot").setLevel(logging.DEBUG)
log = logging.getLogger(__name__)
shutdown_event = threading.Event()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")
SLACK_SIGNING_KEY = os.getenv("SLACK_SIGNING_KEY")
DISCORD_FORWARD_CHANNEL_ID = os.getenv("DISCORD_FORWARD_CHANNEL_ID")

if (
    not DISCORD_TOKEN
    or not SLACK_BOT_TOKEN
    or not SLACK_APP_TOKEN
    or not SLACK_SIGNING_KEY
    or not DISCORD_FORWARD_CHANNEL_ID
):
    log.fatal(
        "DISCORD_TOKEN, SLACK_BOT_TOKEN, SLACK_APP_TOKEN, SLACK_SIGNING_KEY and DISCORD_FORWARD_CHANNEL_ID must be set"
    )
    sys.exit(1)

DISCORD_FORWARD_CHANNEL_ID = int(DISCORD_FORWARD_CHANNEL_ID)


def start_discord_bot(bot: SomeDiscordBot) -> None:
    bot.run(DISCORD_TOKEN)
    shutdown_event.set()


def start_slack_bot(bot: SomeSlackBot) -> None:
    bot.run()
    shutdown_event.set()


def signal_handler(signum: int, frame: Any) -> None:
    print(f"Signal {signum} received, shutting down...")
    shutdown_event.set()


def main() -> None:
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    message_queue = queue.Queue()

    discord_bot = SomeDiscordBot(
        message_queue=message_queue, shutdown_event=shutdown_event, channel_id=DISCORD_FORWARD_CHANNEL_ID
    )
    discord_bot_thread = threading.Thread(
        target=start_discord_bot, args=(discord_bot,), daemon=True, name="discord_bot"
    )
    discord_bot_thread.start()

    slack_bot = SomeSlackBot(
        bot_token=SLACK_BOT_TOKEN,
        app_token=SLACK_APP_TOKEN,
        signing_key=SLACK_SIGNING_KEY,
        message_queue=message_queue,
        forward_user=SLACK_FORWARD_USER,
    )
    slack_bot_thread = threading.Thread(target=start_slack_bot, args=(slack_bot,), daemon=True, name="slack_bot")
    slack_bot_thread.start()

    shutdown_event.wait()
    print("Shutdown complete")


if __name__ == "__main__":
    main()
