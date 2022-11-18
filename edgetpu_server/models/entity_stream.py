"""Container for entity_id and stream."""

# pylint: disable=too-few-public-methods
import cv2


class EntityStream:
    """Data structure for holding entity and stream information."""

    def __init__(self, name, entity_id, stream_url):
        self.name = name
        self.entity_id = entity_id
        self.stream_url = stream_url
        self.video_stream = cv2.VideoCapture(self.stream_url, cv2.CAP_FFMPEG)  # pylint: disable=no-member

        print("CV_CAP_PROP_FRAME_WIDTH: '{}'".format(self.video_stream.get(cv2.CAP_PROP_FRAME_WIDTH)))
        print("CV_CAP_PROP_FRAME_HEIGHT : '{}'".format(self.video_stream.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        print("CAP_PROP_FPS : '{}'".format(self.video_stream.get(cv2.CAP_PROP_FPS)))
        print("CAP_PROP_POS_MSEC : '{}'".format(self.video_stream.get(cv2.CAP_PROP_POS_MSEC)))
        print("CAP_PROP_FRAME_COUNT  : '{}'".format(self.video_stream.get(cv2.CAP_PROP_FRAME_COUNT)))
        print("CAP_PROP_BRIGHTNESS : '{}'".format(self.video_stream.get(cv2.CAP_PROP_BRIGHTNESS)))
        print("CAP_PROP_CONTRAST : '{}'".format(self.video_stream.get(cv2.CAP_PROP_CONTRAST)))
        print("CAP_PROP_SATURATION : '{}'".format(self.video_stream.get(cv2.CAP_PROP_SATURATION)))
        print("CAP_PROP_HUE : '{}'".format(self.video_stream.get(cv2.CAP_PROP_HUE)))
        print("CAP_PROP_GAIN  : '{}'".format(self.video_stream.get(cv2.CAP_PROP_GAIN)))
        print("CAP_PROP_CONVERT_RGB : '{}'".format(self.video_stream.get(cv2.CAP_PROP_CONVERT_RGB)))

