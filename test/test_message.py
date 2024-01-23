from somebot.discord_bot import internal_channels


def test_message():
    assert len(internal_channels) > 0
