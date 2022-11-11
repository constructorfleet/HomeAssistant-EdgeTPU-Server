import logging
from queue import Empty

import cv2

from edgetpu_server.services import Service
from edgetpu_server.services.signals.video_capture import VideoCaptureSignal


class CaptureError(Exception):
    """Error indicating there was an error performing the capture."""


class VideoCaptureService(Service):
    """Service for handling video captures."""

    def __init__(
            self,
            name: str,
            video_stream_url: str,
            capture_signal: VideoCaptureSignal
    ):
        """Initialize a new video capture service."""
        super().__init__(name)
        self.video_stream_url = video_stream_url
        self._signal = capture_signal

    # noinspection PyBroadException
    def run(self):
        """Service entrypoint."""
        video_capture = cv2.VideoCapture(
            self.video_stream_url,
            cv2.CAP_FFMPEG,
        )  # pylint: disable=no-member
        while video_capture.isOpened():
            try:
                if self._signal.is_frame_requested():
                    _, frame = video_capture.retrieve()
                    if frame:
                        self._signal.send_frame(frame)
                        continue
                    _, frame = video_capture.read()
                    if frame:
                        self._signal.send_frame(frame)
                        continue
                    raise CaptureError("Unable to retrieve frame")

                video_capture.grab()
            except CaptureError:
                video_capture.release()
                video_capture.open(
                    self.video_stream_url,
                    cv2.CAP_FFMPEG,
                )
            except:
                # TODO: He's dead Jim
                continue
