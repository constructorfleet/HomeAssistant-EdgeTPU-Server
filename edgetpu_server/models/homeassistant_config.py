class HomeAssistantConfig:
    """Data structure for holding Home-Assistant server configuration."""

    def __init__(self, url, token):
        self.url = url
        self.token = token
