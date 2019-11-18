import logging
import re
import time

from edgetpu_server.detection_engine import DetectionFilter, FilteredDetectionEngine
from edgetpu_server.detection_thread import DetectionThread
from edgetpu_server.homeassistant_api import HomeAssistantApi
from edgetpu_server.models.entity_stream import EntityStream
from edgetpu_server.models.homeassistant_config import HomeAssistantConfig

_LOGGER = logging.getLogger(__name__)

PATTERN_STREAM_INPUT = "^(.+)\\|(.*)$"


def split_stream_from_name(stream):
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


class EdgeTPUServer:
    """EdgeTPU Server."""

    def __init__(
            self,
            model_path,
            label_path,
            labels_to_report,
            confidence,
            streams,
            homeassistant_config,
            start_thread=False
    ):
        labels = _read_label_file(label_path)
        self.engine = FilteredDetectionEngine(
            DetectionFilter(
                confidence,
                labels,
                labels_to_report
            ),
            model_path
        )
        self.threads = []
        self.running = start_thread
        for stream in streams:
            entity_id, stream_url = split_stream_from_name(stream)
            self.threads.append(DetectionThread(
                EntityStream(entity_id, stream_url),
                self.engine,
                HomeAssistantApi(homeassistant_config),
                start_thread
            ))

        if start_thread:
            self.run()

    def run(self):
        if not self.running:
            for thread in self.threads:
                thread.start()
        while True:
            time.sleep(300)
