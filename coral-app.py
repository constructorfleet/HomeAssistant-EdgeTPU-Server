import re
import threading
import logging
import time

from edgetpu.detection.engine import DetectionEngine

from homeassistant import HomeAssistantApi
from video_detect import DetectionThread

LOGGER = logging.getLogger(__name__)

ARG_CONFIDENCE = "confidence"
ARG_HA_URL = "homeassistant"
ARG_LABEL_FILE = "labels"
ARG_MODEL_FILE = "model"
ARG_STREAMS = "streams"
ARG_TOKEN = "token"
ARG_TYPES = "types"
PATTERN_STREAM_INPUT = "^(.+)\\|(.*)$"
DECIMALS = 2  # The number of decimal places data is returned to

engine = None
labels = None
home_assistant = None
threads = []
filename = "snapshot.jpg"


def draw_box(draw, box, img_width, img_height, text="", color=(255, 255, 0)):
    """Draw bounding box on image."""
    ymin, xmin, ymax, xmax = box
    (left, right, top, bottom) = (
        xmin * img_width,
        xmax * img_width,
        ymin * img_height,
        ymax * img_height,
    )
    draw.line(
        [(left, top), (left, bottom), (right, bottom), (right, top), (left, top)],
        width=5,
        fill=color,
    )
    if text:
        draw.text((left, abs(top - 15)), text, fill=color)


def read_label_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        ret = {}
        for line in lines:
            pair = line.strip().split(maxsplit=1)
            ret[int(pair[0])] = pair[1].strip()
    return ret


def load_model(model_file=None, label_file=None):
    """
    Load model and labels.
    """
    global engine, labels

    engine = DetectionEngine(model_file)
    print("\n Loaded engine with model : {}".format(model_file))

    labels = read_label_file(label_file)
    print("\n Loaded labels from file : {}".format(label_file))


def split_stream_from_name(stream_arg):
    match = re.match(PATTERN_STREAM_INPUT, stream_arg)
    if match:
        return match.group(1), match.group(2)
    raise ValueError("Stream input {} does not match pattern 'name|stream'")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Google Coral EdgeTPU video stream detection")
    parser.add_argument("-m", "--{}".format(ARG_MODEL_FILE), required=True,
                        help="path to TensorFlow Lite object detection model")
    parser.add_argument("-l", "--{}".format(ARG_LABEL_FILE), required=True,
                        help="path to labels file")
    parser.add_argument("-c", "--{}".format(ARG_CONFIDENCE), type=float, default=70,
                        help="minimum probability to filter weak detections, percentage")
    parser.add_argument("-s", "--{}".format(ARG_STREAMS), nargs="+", required=True,
                        help="video streams to process (name|stream address)")
    parser.add_argument("-t", "--{}".format(ARG_TYPES), nargs="+", required=False,
                        help="classifier types to report")
    parser.add_argument("-u", "--{}".format(ARG_HA_URL), required=True,
                        help="url for updating home-assistant states")
    parser.add_argument("-a", "--{}".format(ARG_TOKEN), required=True,
                        help="long lived home-assistant token for authentication")
    args = parser.parse_args()

    home_assistant = HomeAssistantApi(args.homeassistant, args.token)
    thread = threading.Thread(target=home_assistant.run)
    thread.daemon = True
    thread.start()
    threads.append(thread)

    load_model(args.model, args.labels)

    for stream_input in args.streams:
        stream_name = "unknown"
        stream_url = "n/a"
        try:
            stream_name, stream_url = split_stream_from_name(stream_input)
            video_detect = DetectionThread(stream_name, stream_url, engine, args.confidence, home_assistant.add_request)

            thread = threading.Thread(target=video_detect.detect)
            thread.daemon = True
            thread.start()
            threads.append(thread)
        except ValueError:
            LOGGER.error("Unable to start detection for {} at {}".format(stream_name, stream_url))

    while True:
        time.sleep(5)

