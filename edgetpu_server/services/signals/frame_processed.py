from multiprocessing import Queue


# TODO: Ensure this works cross threads
class FrameProcessedSignal(object):
    """Allows for thread-safe frame process result communication."""

    def __init__(self):
        """Initiate a new frame process signal."""
        self._process_result = Queue()

    def send_results(
            self,
            results
    ):
        """Signals upstream service to handle results from frame processing."""
        self._process_result.put(results)

    def receive_results(self):
        """Gets the next result in the queue."""
        return self._process_result.get(block=True)
