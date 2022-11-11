import logging
from queue import Empty

import cv2
from multiprocessing.queues import Queue

from edgetpu_server.services import Service
from edgetpu_server.services.signals.frame_processed import FrameProcessedSignal
from edgetpu_server.services.video_capture import VideoCaptureSignal


class FrameProcessService(Service):
    """Service for handling processing of frames."""

    def __init__(self, name: str, capture_signal: VideoCaptureSignal, result_signal: FrameProcessedSignal):
        """Initialize a new video capture service."""
        super().__init__(name)
        self._capture_signal = capture_signal
        self._result_signal = result_signal

    # noinspection PyBroadException
    def run(self):
        """Service entrypoint."""
        while True:
            try:
                self._capture_signal.request_latest_frame()
                frame = self._capture_signal.retrieve_frame()

                result = {}
                self._result_signal.send_results(result)
            except Exception:
                # TODO : He's dead jim
                continue
