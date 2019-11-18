"""Container for entity_id and stream."""

# pylint: disable=too-few-public-methods
import cv2


class EntityStream:
    """Data structure for holding entity and stream information."""

    def __init__(self, entity_id, stream_url):
        self.entity_id = entity_id
        self.stream_url = stream_url
        self.video_stream = \
            cv2.VideoCapture(self.stream_url)  # pylint: disable=no-member
