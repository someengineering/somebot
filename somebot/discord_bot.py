import asyncio
import logging
import discord
import time
import threading
import queue
from .util import convert_slack_message_to_discord


log = logging.getLogger(__name__)

internal_channels = ("ui-internal", "dev-internal")
nag_message = "Are you sure this is an internal message? Don't forget to use the public channel!"
threshold = 32
remind_every = 60 * 15


class SomeDiscordBot(discord.Client):
    def __init__(self, *args, message_queue: queue.Queue, shutdown_event: threading.Event, channel_id: int, **kwargs):
        kwargs.update({"intents": discord.Intents.all()})
        super().__init__(*args, **kwargs)
        self.message_queue = message_queue
        self.shutdown_event = shutdown_event
        self.last_reminded = {}
        self.discord_channel_id = channel_id

    async def on_ready(self):
        log.info(f"{self.user.name} has connected to Discord!")
        asyncio.create_task(self.process_message_queue())

    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            return

        if (
            message.channel.name in internal_channels
            and len(message.content) > threshold
            and (
                message.author.id not in self.last_reminded
                or time.time() - self.last_reminded.get(message.author.id, 0) > remind_every
            )
        ):
            log.debug(f"Message from {message.author} in internal channel")
            await message.channel.send(f"{message.author.mention} {nag_message}")
            self.last_reminded[message.author.id] = time.time()

    async def process_message_queue(self):
        log.debug("Waiting for message from queue")
        while not self.shutdown_event.is_set():
            try:
                message = await asyncio.to_thread(self.message_queue.get, timeout=3)
                log.debug(f"Got message from queue: {message}")
                message = convert_slack_message_to_discord(message)
                channel = self.get_channel(self.discord_channel_id)
                if channel:
                    log.debug(f"Sending message to {channel}")
                    await channel.send(content=message.get("content"), embeds=message.get("embeds", []))
            except queue.Empty:
                pass
