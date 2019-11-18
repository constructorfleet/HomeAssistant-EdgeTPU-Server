import logging
import re
import time

from edgetpu_server.detection_engine import DetectionFilter, FilteredDetectionEngine
from edgetpu_server.detection_thread import DetectionThread
from edgetpu_server.homeassistant_api import HomeAssistantApi
from edgetpu_server.models.homeassistant_config import HomeAssistantConfig

_LOGGER = logging.getLogger(__name__)

PATTERN_STREAM_INPUT = "^(.+)\\|(.*)$"


def split_stream_from_name(stream_arg):
    match = re.match(PATTERN_STREAM_INPUT, stream_arg)
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

    __slots__ = ['engine', 'hass', 'threads', 'running']

    def __init__(
            self,
            model_path,
            label_path,
            labels_to_report,
            confidence,
            entity_streams,
            homeassistant_config,
            start_thread=False
    ):
        labels = _read_label_file(label_path)
        self.engine = FilteredDetectionEngine(
            DetectionFilter(
                labels,
                labels_to_report,
                confidence
            ),
            model_path
        )
        self.threads = []
        self.running = start_thread
        for entity_stream in entity_streams:
            self.threads.append(DetectionThread(
                entity_stream,
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

