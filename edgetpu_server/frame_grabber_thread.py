"""Frame grabber thread."""
import logging

_LOGGER = logging.getLogger(__name__)


# pylint: disable=too-few-public-methods
class FrameGrabberThread:
    """Thread that continually grabs frames from a video stream."""

    def __init__(self, video_stream, video_stream_lock):
        _LOGGER.warn('Initializing frame grabber')
        self._video_stream = video_stream
        self._video_stream_lock = video_stream_lock

    def run(self):
        """Continuously grab the latest frame from the video stream."""
        _LOGGER.warn('Running FrameGrabber thread')
        while self._video_stream.isOpened():
            _LOGGER.debug("Acquiring lock")
            self._video_stream_lock.acquire()
            try:
                _LOGGER.debug("Grabbing Frame")
                self._video_stream.grab()
            except:
                _LOGGER.warn("Error grabbing frame")
            finally:
                self._video_stream_lock.release()
        _LOGGER.warn('Video stream closed')
