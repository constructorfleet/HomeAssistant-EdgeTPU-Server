class Service(object):
    """Base class for all services."""

    def __init__(
            self,
            name: str,
    ):
        """Initialize a new service."""
        self._name = name

    @property
    def name(self):
        """Get the name of the service instance."""
        return self._name
