"""Main entry point for edgetpu-server script."""
import os
import re
import sys

import configargparse

from edgetpu_server import EdgeTPUServer, HomeAssistantConfig, EntityStream

REGEX_ENTITY_STREAM_NAME = re.compile(r'^([a-z0-9_]+):')
REGEX_VIDEO_STREAM = re.compile(r'^\W+stream: (.*)$')
REGEX_SENSOR_ID = re.compile(r'^\W+entity_id: (sensor\.[a-z_]*)$')


def _load_stream_files(stream_files):
    entity_streams = []
    for file in stream_files:
        line_number = 0
        entity_stream_name = None
        stream = None
        sensor = None
        if not os.path.exists(file):
            raise FileExistsError('The file %s does not exists' % file)
        with open(file, 'r') as reader:
            for line in reader.readlines():
                line_number += 1
                if len(line) == 0:
                    continue
                match_name = re.match(REGEX_ENTITY_STREAM_NAME, line)
                match_sensor = re.match(REGEX_SENSOR_ID, line)
                match_stream = re.match(REGEX_VIDEO_STREAM, line)
                if entity_stream_name is None and match_name is not None:
                    entity_stream_name = match_name.group(1)
                    continue
                elif entity_stream_name is None and (match_sensor or match_stream):
                    raise ValueError(
                        'Invalid format in %s on line %d: '
                        'entity stream name much prescede sensor and stream' % (
                            file, line_number))
                elif entity_stream_name is not None:
                    if stream is not None and match_stream is not None:
                        raise ValueError(
                            'Invalid format in %s on line %d: stream is already set' % (
                                file, line_number))
                    elif stream is None and match_stream is not None:
                        stream = match_stream.group(1)

                    if sensor is not None and match_sensor is not None:
                        raise ValueError(
                            'Invalid format in %s on line %d: stream is already set' % (
                                file, line_number))
                    elif sensor is None and match_sensor is not None:
                        sensor = match_sensor.group(1)

                if None not in [entity_stream_name, sensor, stream]:
                    entity_streams.append(
                        EntityStream(
                            entity_stream_name,
                            entity_id=sensor,
                            stream_url=stream))
                    entity_stream_name = stream = sensor = None

    return entity_streams


def main():
    """Start the edgetpu server."""
    parser = configargparse.ArgParser(
        description="Google EdgeTPU video stream detection"
    )
    parser.add_argument('-f', '--config-file', is_config_file=True,
                        help="Configuration file path")
    parser.add_argument("--models", required=True,
                        help="path to TensorFlow Lite object detection model")
    parser.add_argument("--labels", required=True,
                        help="path to labels file")
    parser.add_argument("--confidence", type=float, default=70,
                        help="minimum probability to filter weak detections, percentage")
    parser.add_argument("--streams", nargs="+", required=True,
                        help="Paths to video stream configuration files to process")
    parser.add_argument("--categories", nargs="+", required=False,
                        help="classifier types to report")
    parser.add_argument("--ha-url", required=True,
                        help="url for updating home-assistant states")
    parser.add_argument("--token", required=True,
                        help="long lived home-assistant token for authentication")
    args = parser.parse_args()

    try:
        entity_streams = _load_stream_files(args.streams)
    except:
        sys.exit(5)

    EdgeTPUServer(
        args.models,
        args.labels,
        args.categories,
        args.confidence,
        entity_streams,
        HomeAssistantConfig(
            args.ha_url,
            args.token
        )
    )


if __name__ == '__main__':
    sys.exit(main())
