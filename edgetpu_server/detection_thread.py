import cv2
from datetime import datetime
import time
import imutils
import logging
from PIL import Image
from threading import Thread

from edgetpu_server.models.detection_entity import DetectionEntity

_LOGGER = logging.getLogger(__name__)

DEFAULT_WIDTH = 500
FRAME_FAILURE_SLEEP = 0.5


class DetectionThread(Thread):
    """Image detection thread."""

    def __init__(self, entity_stream, engine, hass, start_thread):
        Thread.__init__(self, target=self.run())
        self.entity_stream = entity_stream
        self.engine = engine
        self.hass = hass
        self.daemon = True
        if start_thread:
            self.start()

    def _retrieve_frame(self):
        start = datetime.now()
        video_stream = cv2.VideoCapture(self.entity_stream.stream_url)
        try:
            ret, frame = video_stream.read()
        except Exception as err:
            _LOGGER.error("Error retrieving video frame: %s",
                          str(err))
            return None

        if not ret or not frame:
            return None

        frame = cv2.cvtColor(
            imutils.resize(
                frame,
                width=DEFAULT_WIDTH
            ),
            cv2.COLOR_BGR2RGB
        )

        _LOGGER.debug(
            "Retrieving frame took %d ms time for %s (%s)",
            datetime.now() - start,
            self.entity_stream.entity_id,
            self.entity_stream.stream_url
        )

        return frame

    def _process_frame(self, frame):
        start = datetime.now()
        detection_entity = DetectionEntity(
            self.entity_stream.entity_id,
            self.engine.filtered_detect_with_image(frame)
        )

        _LOGGER.debug(
            "Processing frame took %d ms time for %s (%s)",
            datetime.now() - start,
            self.entity_stream.entity_id,
            self.entity_stream.stream_url
        )

        return detection_entity

    def _set_state(self, detection_entity):
        start = datetime.now()
        try:
            self.hass.set_entity_state(detection_entity)
        except Exception as err:
            _LOGGER.error(
                "Error setting entity state %s: %s",
                detection_entity.entity_id,
                str(err)
            )

        _LOGGER.debug(
            "Setting entity state took %d ms time for %s (%s)",
            datetime.now() - start,
            self.entity_stream.entity_id,
            self.entity_stream.stream_url
        )

    def run(self):
        """Loop through video stream frames and detect objects."""
        while True:
            start = datetime.now()
            frame = self._retrieve_frame()
            if not frame:
                _LOGGER.warning(
                    "Unable to retrieve frame, sleeping for %f s",
                    FRAME_FAILURE_SLEEP
                )
                time.sleep(FRAME_FAILURE_SLEEP)
                continue

            detection_entity = self._process_frame(frame)

            self._set_state(detection_entity)

            _LOGGER.debug(
                "Detection loop took %d ms time for %s (%s)",
                datetime.now() - start,
                self.entity_stream.entity_id,
                self.entity_stream.stream_url
            )


