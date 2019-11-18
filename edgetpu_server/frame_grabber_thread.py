"""Frame grabber thread."""
import time
import logging
from threading import Thread

_LOGGER = logging.getLogger(__name__)


class FrameGrabberThread(Thread):
    """Thread that continually grabs frames from a video stream."""

    def __init__(self, video_stream, lock):
        self._video_stream = video_stream
        self.lock = lock
        Thread.__init__(self, target=self.run())
        self.daemon = True
        self.start()

    def run(self):
        """Continuously grab the latest frame from the video stream."""
        while True:
            # if self.lock.locked():
            #     _LOGGER.warning("Locked, waiting...")
            #     time.sleep(0.01)
            with self.lock:
                _LOGGER.warning("Grabbing frame")
                self._video_stream.grab()
