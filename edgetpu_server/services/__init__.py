from edgetpu_server.services.signals.exception_thrown import ExceptionThrownSignal


class Service(object):
    """Base class for all services."""

    def __init__(
            self,
            name: str,
            exception_thrown_signal: ExceptionThrownSignal,
    ):
        """Initialize a new service."""
        self._name = name
        self._exception_thrown_signal = exception_thrown_signal

    @property
    def name(self):
        """Get the name of the service instance."""
        return self._name

    def signal_exception(self, error: Exception):
        """Put an exception into the queue."""
        self._exception_thrown_signal.send_exception(
            self.name,
            error
        )
