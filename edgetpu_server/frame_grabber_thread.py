"""Frame grabber thread."""
import logging

_LOGGER = logging.getLogger(__name__)


# pylint: disable=too-few-public-methods
class FrameGrabberThread:
    """Thread that continually grabs frames from a video stream."""

    def __init__(self, video_stream, lock):
        self._video_stream = video_stream
        self.lock = lock

    def run(self):
        """Continuously grab the latest frame from the video stream."""
        while self._video_stream.isOpened():
            self.lock.acquire()
            try:
                self._video_stream.grab()
            except:
                _LOGGER.info("Error grabbing frame")
            self.lock.release()
