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
from .bot import SomeBot


log_format = "%(asctime)s - %(levelname)s - %(threadName)s - %(message)s"
logging.basicConfig(level=logging.WARN, format=log_format)
logging.getLogger("somebot").setLevel(logging.DEBUG)
log = logging.getLogger(__name__)

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    log.fatal("DISCORD_TOKEN must be set")
    sys.exit(1)


def main() -> None:
    bot = SomeBot()
    bot.run(TOKEN)


if __name__ == "__main__":
    main()
