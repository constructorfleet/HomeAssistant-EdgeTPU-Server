"""Thread for processing object detection."""
import logging
import time
from datetime import datetime
from threading import Thread

import cv2
import imutils
from PIL import Image

from edgetpu_server.models.detection_entity import DetectionEntity

_LOGGER = logging.getLogger(__name__)

DEFAULT_WIDTH = 500
FRAME_FAILURE_SLEEP = 0.5


class DetectionThread(Thread):
    """Image detection thread."""

    def __init__(self, entity_stream, engine, hass, start_thread):
        self.entity_stream = entity_stream
        self.engine = engine
        self.hass = hass
        Thread.__init__(self, target=self.run())
        self.daemon = True
        if start_thread:
            self.start()

    def _retrieve_frame(self):
        start = datetime.now().timestamp()
        _LOGGER.warning("Stream %s",
                        self.entity_stream.stream_url)
        video_stream = \
            cv2.VideoCapture(self.entity_stream.stream_url)  # pylint: disable=no-member
        try:
            ret, frame = video_stream.read()
        except Exception as err:
            _LOGGER.error("Error retrieving video frame: %s",
                          str(err))
            return None

        if not ret:
            return None

        frame = cv2.cvtColor(   # pylint: disable=no-member
            imutils.resize(
                frame,
                width=DEFAULT_WIDTH
            ),
            cv2.COLOR_BGR2RGB  # pylint: disable=no-member
        )  # pylint: disable=no-member

        _LOGGER.warning(
            "Retrieving frame took %f ms time for %s (%s)",
            (datetime.now().timestamp()) - start,
            self.entity_stream.entity_id,
            self.entity_stream.stream_url
        )

        return Image.fromarray(frame)

    def _process_frame(self, frame):
        start = datetime.now().timestamp()
        detection_entity = DetectionEntity(
            self.entity_stream.entity_id,
            self.engine.filtered_detect_with_image(frame)
        )

        _LOGGER.warning(
            "Processing frame took %f ms time for %s (%s)",
            datetime.now().timestamp() - start,
            self.entity_stream.entity_id,
            self.entity_stream.stream_url
        )

        return detection_entity

    def _set_state(self, detection_entity):
        start = datetime.now().timestamp()
        try:
            self.hass.set_entity_state(detection_entity)
        except Exception as err:
            _LOGGER.error(
                "Error setting entity state %s: %s",
                detection_entity.entity_id,
                str(err)
            )

        _LOGGER.warning(
            "Setting entity state took %f ms time for %s (%s)",
            datetime.now().timestamp() - start,
            self.entity_stream.entity_id,
            self.entity_stream.stream_url
        )

    def run(self):
        """Loop through video stream frames and detect objects."""
        while True:
            start = datetime.now().timestamp()
            frame = self._retrieve_frame()
            if frame is None:
                _LOGGER.warning(
                    "Unable to retrieve frame, sleeping for %f s",
                    FRAME_FAILURE_SLEEP
                )
                time.sleep(FRAME_FAILURE_SLEEP)
                continue

            detection_entity = self._process_frame(frame)

            self._set_state(detection_entity)

            _LOGGER.warning(
                "Detection loop took %f ms time for %s (%s)",
                datetime.now().timestamp() - start,
                self.entity_stream.entity_id,
                self.entity_stream.stream_url
            )
