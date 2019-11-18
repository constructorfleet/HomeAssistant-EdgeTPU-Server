"""Main entry point for edgetpu-server script."""
import argparse
import sys

from edgetpu_server import EdgeTPUServer, HomeAssistantConfig


def main():
    """Start the edgetpu server."""
    parser = argparse.ArgumentParser(
        description="Google Coral EdgeTPU video stream detection")
    parser.add_argument("-m", "--models", required=True,
                        help="path to TensorFlow Lite object detection model")
    parser.add_argument("-l", "--labels", required=True,
                        help="path to labels file")
    parser.add_argument("-c", "--confidence", type=float, default=70,
                        help="minimum probability to filter weak detections, percentage")
    parser.add_argument("-s", "--streams", nargs="+", required=True,
                        help="video streams to process (name|stream address)")
    parser.add_argument("-t", "--categories", nargs="+", required=False,
                        help="classifier types to report")
    parser.add_argument("-u", "--haurl", required=True,
                        help="url for updating home-assistant states")
    parser.add_argument("-a", "--token", required=True,
                        help="long lived home-assistant token for authentication")
    args = parser.parse_args()

    EdgeTPUServer(
        args.models,
        args.labels,
        args.categories,
        args.confidence,
        args.streams,
        HomeAssistantConfig(
            args.haurl,
            args.token
        )
    )


if __name__ == '__main__':
    sys.exit(main())
