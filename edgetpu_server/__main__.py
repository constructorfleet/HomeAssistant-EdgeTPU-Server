"""Main entry point for edgetpu-server script."""
import sys

import configargparse

from edgetpu_server import EdgeTPUServer, HomeAssistantConfig, EntityStream


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
    parser.add_argument("--stream", required=True,
                        help="video stream to process")
    parser.add_argument("--entity", required=True,
                        help="Entity ID to push to Home-Assistant")
    parser.add_argument("--categories", nargs="+", required=False,
                        help="classifier types to report")
    parser.add_argument("--haurl", required=True,
                        help="url for updating home-assistant states")
    parser.add_argument("--token", required=True,
                        help="long lived home-assistant token for authentication")
    args = parser.parse_args()

    EdgeTPUServer(
        args.models,
        args.labels,
        args.categories,
        args.confidence,
        EntityStream(
            args.entity,
            args.stream
        ),
        HomeAssistantConfig(
            args.haurl,
            args.token
        )
    )


if __name__ == '__main__':
    sys.exit(main())
