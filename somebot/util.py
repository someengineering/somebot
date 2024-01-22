import re
from discord import Embed
from typing import Any


def truncate(text, limit):
    return text if len(text) <= limit else text[: limit - 3] + "..."


def convert_slack_link_to_discord(text):
    return re.sub(r"<(http[^|]+)\|([^>]+)>", r"[\2](\1)", text)


def convert_slack_message_to_discord(slack_message: dict[str, Any]):
    discord_message = {"content": truncate(slack_message.get("text", ""), 2000), "embeds": []}

    for attachment in slack_message.get("attachments", []):
        embed = {}
        if "title" in attachment:
            embed["title"] = truncate(attachment["title"], 256)
        if "text" in attachment:
            embed["description"] = truncate(convert_slack_link_to_discord(attachment["text"]), 4096)
        if "title_link" in attachment:
            embed["url"] = attachment["title_link"]
        if "color" in attachment:
            embed["color"] = int(attachment["color"], 16)
        discord_message["embeds"].append(Embed.from_dict(embed))

    return discord_message
