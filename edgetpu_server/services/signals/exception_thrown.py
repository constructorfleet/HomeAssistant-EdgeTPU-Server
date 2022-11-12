from multiprocessing import Queue


class ExceptionThrownSignal:
    """Signal to bubble runtime errors."""

    def __init__(self):
        """Instantiate a new thrown exception signal."""
        self._exception_thrown = Queue()

    def send_exception(
            self,
            service_name: str,
            error: Exception,
    ):
        """Signal an exception was encountered."""
        self._exception_thrown.put({
            "name": service_name,
            "error": error
        })
