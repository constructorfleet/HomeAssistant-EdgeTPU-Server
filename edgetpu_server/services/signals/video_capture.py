from multiprocessing import Queue
from queue import Empty


# TODO: Ensure this works cross threads
class VideoCaptureSignal(object):
    """Allows for bidirectional thread-safe communication."""

    def __init__(self):
        """Initialize a new duplex queue."""
        self._image_request = Queue(
            maxsize=1,
        )
        self._image_response = Queue(
            maxsize=1,
        )

    def request_latest_frame(self):
        """Notify capture service to retrieve next frame."""
        self._image_request.put(True)

    def is_frame_requested(self):
        """Checks if a request for the next frame has been made."""
        try:
            return self._image_request.get_nowait()
        except Empty:
            return False

    def send_frame(self, frame):
        """Send latest frame upstream."""
        self._image_response.put(frame)

    def retrieve_frame(self):
        """Retrieves the requested frame."""
        return self._image_response.get(block=True)
