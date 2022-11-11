"""Configuration for HomeAssistant connection"""


# pylint: disable=too-few-public-methods
class HomeAssistantConfig:
    """Data structure for holding Home-Assistant server configuration."""

    def __init__(self, url: str, token: str):
        """Initialize a new home-assistant configuration model."""
        self.url = url
        self.token = token
