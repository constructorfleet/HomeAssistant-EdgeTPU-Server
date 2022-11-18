"""EdgeTPU Server Module."""
import logging
import re
import threading
import time
import queue
from threading import Lock

from edgetpu_server.detection_engine import DetectionFilter, FilteredDetectionEngine
from edgetpu_server.classification_engine import ClassificationFilter, FilteredClassificationEngine
from edgetpu_server.detection_thread import DetectionThread
from edgetpu_server.frame_grabber_thread import FrameGrabberThread
from edgetpu_server.homeassistant_api import HomeAssistantApi
from edgetpu_server.image_server import get_app
from edgetpu_server.models.entity_stream import EntityStream
from edgetpu_server.models.homeassistant_config import HomeAssistantConfig
import cv2
logging.basicConfig(level=logging.DEBUG)
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


class VideoCapture:

  def __init__(self, name):
    self.cap = cv2.VideoCapture(name)
    self.q = queue.Queue()
    t = threading.Thread(target=self._reader)
    t.daemon = True
    t.start()

  # read frames as soon as they are available, keeping only most recent one
  def _reader(self):
    while True:
      ret, frame = self.cap.read()
      if not ret:
        break
      if not self.q.empty():
        try:
          self.q.get_nowait()   # discard previous (unprocessed) frame
        except queue.Empty:
          pass
      self.q.put(frame)

  def retrieve(self):
    return self.q.get()


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
        _LOGGER.error(entity_streams)
        # self.app = get_app()
        # self.port = port
        labels = _read_label_file(label_path)
        detection_lock = Lock()
        self.engine = FilteredClassificationEngine(
            ClassificationFilter(
                confidence,
                labels,
                labels_to_report
            ),
            model_path,
            detection_lock
        )
        self.running = True

        for entity_stream in entity_streams:
            _LOGGER.error("Creating frame grabber read")
            # video_stream_lock = queue.Queue()
            # frame_grabber = FrameGrabberThread(
            #     entity_stream.video_stream,
            #     video_stream_lock
            # )
            # grabber_thread = threading.Thread(target=frame_grabber.run)
            # grabber_thread.start()
            cap = VideoCapture(entity_stream.video_stream)

            detection = DetectionThread(
                # self.app.set_image_data,
                entity_stream,
                self.engine,
                HomeAssistantApi(homeassistant_config),
                cap
            )
            thread = threading.Thread(target=detection.run)
            thread.start()

        self.run()

    def run(self):
        """Start application loop."""
        # self.app.run(host="0.0.0.0", port=self.port)
        while True:
            time.sleep(1000)
