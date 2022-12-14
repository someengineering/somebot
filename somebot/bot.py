# Copyright 2020 Lukas Lösche <lloesche@fedoraproject.org>
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
import logging
import discord
import time


log = logging.getLogger(__name__)

internal_channels = ("ui-internal", "dev-internal")
nag_message = (
    "Are you sure this is an internal message? Don't forget to use the public channel!"
)
threshold = 32
remind_every = 60 * 15


class SomeBot(discord.Client):
    def __init__(self, *args, **kwargs):
        kwargs.update({"intents": discord.Intents.all()})
        super().__init__(*args, **kwargs)
        self.last_reminded = {}

    async def on_ready(self):
        log.info(f"{self.user.name} has connected to Discord!")

    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            return

        if (
            message.channel.name in internal_channels
            and len(message.content) > threshold
            and (
                message.author.id not in self.last_reminded
                or time.time() - self.last_reminded.get(message.author.id, 0)
                > remind_every
            )
        ):
            log.debug(f"Message from {message.author} in internal channel")
            await message.channel.send(f"{message.author.mention} {nag_message}")
            self.last_reminded[message.author.id] = time.time()
