class HomeAssistantConfig:
    """Data structure for holding Home-Assistant server configuration."""

    __slots__ = ['url', 'token']

    def __init__(self, url, token):
        self.url = url
        self.token = token
