"""Thread for processing object detection."""
import logging
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

    def __init__(self, entity_stream, engine, hass, cap):
        # self._set_image_data = set_image_data
        self.entity_stream = entity_stream
        self.engine = engine
        self.hass = hass
        self.video_url = entity_stream.stream_url
        self.video_stream = entity_stream.video_stream
        self.cap = cap

    def _retrieve_frame(self):
        ret = None
        frame = None
        start = datetime.now().timestamp()
        _LOGGER.debug("Acquiring lock")
        # self.video_stream_lock.acquire()
        try:
            _LOGGER.debug("Retrieving Frame")
            frame = self.cap.retrieve()
        except Exception as err:
            _LOGGER.error("Error retrieving video frame: %s",
                          str(err))
        finally:
            _LOGGER.error("Lock released")
            # self.video_stream_lock.release()

        if frame is None:
            _LOGGER.error(frame)
            return None

        frame = cv2.cvtColor(  # pylint: disable=no-member
            imutils.resize(
                frame,
                width=DEFAULT_WIDTH
            ),
            cv2.COLOR_BGR2RGB  # pylint: disable=no-member
        )  # pylint: disable=no-member
        _LOGGER.error("Resized")
        _LOGGER.debug(
            "Retrieving frame took %f ms time for %s (%s)",
            (datetime.now().timestamp()) - start,
            self.entity_stream.entity_id,
            self.entity_stream.stream_url
        )

        return Image.fromarray(frame) #, Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

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
        _LOGGER.warn('Running detection thread')
        if self.video_stream.isOpened():
            self.video_stream.grab()
        while self.video_stream.isOpened():
            start = datetime.now().timestamp()
            frame = self._retrieve_frame()
            # if original is None:
            #     _LOGGER.warning(
            #         "Unable to get original frame for %s",
            #         self.video_url
            #     )
            if frame is None:
                _LOGGER.warning(
                    "Unable to retrieve frame %s, sleeping for %f s",
                    self.video_url,
                    FRAME_FAILURE_SLEEP
                )
                time.sleep(FRAME_FAILURE_SLEEP)
                continue

            detection_entity = self._process_frame(frame)

            self._set_state(detection_entity)
            # self._annotate_image(original, detection_entity)

            _LOGGER.debug(
                "Detection loop took %f ms time for %s (%s)",
                datetime.now().timestamp() - start,
                self.entity_stream.entity_id,
                self.entity_stream.stream_url
            )
        _LOGGER.warn('Video stream closed')

    # def _annotate_image(self, frame, detection_entity):
    #     image_writer = ImageWriterThread(
    #         self._set_image_data,
    #         frame,
    #         detection_entity
    #     )
    #
    #     image_writer = Process(target=image_writer.run, daemon=True)
    #     image_writer.start()
