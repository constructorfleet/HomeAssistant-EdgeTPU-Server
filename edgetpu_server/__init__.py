"""EdgeTPU Server Module."""
import logging
import re
import time
from threading import Lock
from multiprocessing import Process

from edgetpu_server.classifiers.edgetpu.detection_factory import DetectionFilter, FilteredDetectionEngine
from edgetpu_server.detection_thread import DetectionThread
from edgetpu_server.frame_grabber_thread import FrameGrabberThread
from edgetpu_server.homeassistant_api import HomeAssistantApi
from edgetpu_server.image_server import get_app
from edgetpu_server.models.ImageProcessingEntityData import EntityStream
from edgetpu_server.models.homeassistant_config import HomeAssistantConfig

_LOGGER = logging.getLogger(__name__)

PATTERN_STREAM_INPUT = "^(.+)\\|(.*)$"


def _split_stream_from_name(stream):
    match = re.match(PATTERN_STREAM_INPUT, stream)
    if match:
        return match.group(1), match.group(2)
    raise ValueError("Stream input {} does not match pattern 'name|stream'")


def _read_label_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        labels = {}
        for line in lines:
            pair = line.strip().split(maxsplit=1)
            labels[int(pair[0])] = pair[1].strip()
    return labels


# pylint: disable=too-few-public-methods
class EdgeTPUServer:
    """EdgeTPU Server."""

    # pylint: disable=too-many-arguments,too-many-locals
    def __init__(
            self,
            model_path,
            label_path,
            labels_to_report,
            confidence,
            entity_streams,
            homeassistant_config,
            port
    ):
        # self.app = get_app()
        # self.port = port
        labels = _read_label_file(label_path)
        detection_lock = Lock()
        self.engine = FilteredDetectionEngine(
            DetectionFilter(
                confidence,
                labels,
                labels_to_report
            ),
            model_path,
            detection_lock
        )
        self.running = True

        for entity_stream in entity_streams:
            video_stream_lock = Lock()
            frame_grabber = FrameGrabberThread(
                entity_stream.video_stream,
                video_stream_lock
            )
            grabber_thread = Process(target=frame_grabber.run, daemon=True)
            grabber_thread.start()

            detection = DetectionThread(
                # self.app.set_image_data,
                entity_stream,
                self.engine,
                HomeAssistantApi(homeassistant_config),
                video_stream_lock
            )
            thread = Process(target=detection.run, daemon=True)
            thread.start()

        self.run()

    def run(self):
        """Start application loop."""
        # self.app.run(host="0.0.0.0", port=self.port)
        while True:
            time.sleep(1000)
