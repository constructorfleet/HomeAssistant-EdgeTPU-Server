"""Thread for processing object detection."""
import logging
import threading
import time
from datetime import datetime

import cv2
import imutils
from PIL import Image

from edgetpu_server.image_writer_thread import ImageWriterThread
from edgetpu_server.models.detection_entity import DetectionEntity

_LOGGER = logging.getLogger(__name__)

DEFAULT_WIDTH = 500
FRAME_FAILURE_SLEEP = 0.5
CV_CAP_PROP_FRAME_COUNT = 7
CV_CAP_PROP_POS_FRAMES = 1


# pylint: disable=too-few-public-methods
class DetectionThread:
    """Image detection thread."""

    def __init__(self, entity_stream, engine, hass, video_stream_lock):
        self.entity_stream = entity_stream
        self.engine = engine
        self.hass = hass
        self.video_stream = entity_stream.video_stream
        self.video_stream_lock = video_stream_lock

    def _retrieve_frame(self):
        start = datetime.now().timestamp()
        self.video_stream_lock.acquire()
        try:
            ret, frame = self.video_stream.retrieve()
        except Exception as err:
            _LOGGER.error("Error retrieving video frame: %s",
                          str(err))
            return None
        finally:
            self.video_stream_lock.release()

        if not ret:
            return None

        frame = cv2.cvtColor(  # pylint: disable=no-member
            imutils.resize(
                frame,
                width=DEFAULT_WIDTH
            ),
            cv2.COLOR_BGR2RGB  # pylint: disable=no-member
        )  # pylint: disable=no-member

        _LOGGER.debug(
            "Retrieving frame took %f ms time for %s (%s)",
            (datetime.now().timestamp()) - start,
            self.entity_stream.entity_id,
            self.entity_stream.stream_url
        )

        return (Image.fromarray(frame),
                Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))

    def _process_frame(self, frame):
        start = datetime.now().timestamp()
        try:
            detection_entity = DetectionEntity(
                self.entity_stream.name,
                self.entity_stream.entity_id,
                self.engine.filtered_detect_with_image(frame)
            )
        except Exception as err:
            _LOGGER.error(
                "Error processing frame: %s",
                str(err)
            )

        _LOGGER.debug(
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

        _LOGGER.debug(
            "Setting entity state took %f ms time for %s (%s)",
            datetime.now().timestamp() - start,
            self.entity_stream.entity_id,
            self.entity_stream.stream_url
        )

    def run(self):
        """Loop through video stream frames and detect objects."""
        _LOGGER.info('Running detection thread')
        while self.video_stream.isOpened():
            start = datetime.now().timestamp()
            frame, original = self._retrieve_frame()

            if frame is None:
                _LOGGER.warning(
                    "Unable to retrieve frame, sleeping for %f s",
                    FRAME_FAILURE_SLEEP
                )
                time.sleep(FRAME_FAILURE_SLEEP)
                continue

            detection_entity = self._process_frame(frame)

            self._set_state(detection_entity)
            self._annotate_image(original, detection_entity)

            _LOGGER.debug(
                "Detection loop took %f ms time for %s (%s)",
                datetime.now().timestamp() - start,
                self.entity_stream.entity_id,
                self.entity_stream.stream_url
            )
        _LOGGER.info('Video stream closed')

    def _annotate_image(self, frame, detection_entity):
        image_writer = ImageWriterThread(
            frame,
            detection_entity
        )

        image_writer = threading.Thread(target=image_writer.run)
        image_writer.setDaemon(True)
        image_writer.start()
