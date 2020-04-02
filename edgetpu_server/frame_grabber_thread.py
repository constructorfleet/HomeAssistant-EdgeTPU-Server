"""Frame grabber thread."""
import logging

_LOGGER = logging.getLogger(__name__)


# pylint: disable=too-few-public-methods
class FrameGrabberThread:
    """Thread that continually grabs frames from a video stream."""

    def __init__(self, video_stream, video_stream_lock):
        _LOGGER.info('Initializing frame grabber')
        self._video_stream = video_stream
        self._video_stream_lock = video_stream_lock

    def run(self):
        """Continuously grab the latest frame from the video stream."""
        _LOGGER.info('Running FrameGrabber thread')
        while self._video_stream.isOpened():
            self._video_stream_lock.acquire()
            try:
                self._video_stream.grab()
            except:
                _LOGGER.info("Error grabbing frame")
            finally:
                self._video_stream_lock.release()
        _LOGGER.info('Video stream closed')
