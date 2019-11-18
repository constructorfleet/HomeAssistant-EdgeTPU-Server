"""Frame grabber thread."""
import time
import logging
from threading import Thread

_LOGGER = logging.getLogger(__name__)


class FrameGrabberThread(Thread):
    """Thread that continually grabs frames from a video stream."""

    def __init__(self, video_stream):
        self._video_stream = video_stream
        self.interrupt = False
        Thread.__init__(self, target=self.run())
        self.daemon = True
        self.start()

    def run(self):
        """Continuously grab the latest frame from the video stream."""
        while not self.interrupt and self._video_stream.isOpened():
            self._video_stream.grab()
