import cv2
import time
import imutils
import logging
from PIL import Image

LOGGER = logging.getLogger(__name__)

ATTR_SCORE = "score"
ATTR_BOX = "box"


class DetectionThread:
    _name = None
    _video_stream = None
    _detection_engine = None
    _confidence = None
    _labels = None
    _add_request = None

    def __init__(self, name, stream_url, detection_engine, confidence, labels, add_request):
        self._detection_engine = detection_engine
        self._name = name
        self._video_stream = cv2.VideoCapture(stream_url)
        self._stream_url = stream_url
        self._confidence = confidence
        self._labels = labels
        self._add_request = add_request
        time.sleep(5.0)

    def detect(self):
        # loop over the frames from the video stream
        while True:
            # grab the frame from the threaded video stream and resize it
            # to have a maximum width of 500 pixels
            ret, frame = self._video_stream.read()
            if not ret:
                self._video_stream = cv2.VideoCapture(self._stream_url)
                continue

            frame = imutils.resize(frame, width=500)
            orig = frame.copy()

            # prepare the frame for object detection by converting (1) it
            # from BGR to RGB channel ordering and then (2) from a NumPy
            # array to PIL image format
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = Image.fromarray(frame)

            # make predictions on the input frame
            start = time.time()
            results = self._detection_engine.DetectWithImage(frame, threshold=self._confidence / 100,
                                                             keep_aspect_ratio=True, relative_coord=False)
            end = time.time()
            LOGGER.info("Detection time or {}: {} s".format(self._name, (end - start)))

            matches = {}
            total_matches = 0
            for r in results:
                label = self._labels.get(r.label_id, None)
                if not label:
                    continue

                score = r.score * 100
                if label not in matches:
                    matches[label] = []

                box = r.bounding_box.flatten().astype("int")
                matches[label].append({
                    ATTR_SCORE: score,
                    ATTR_BOX: list(box)
                })
                total_matches += 1

            self._add_request(self._name, matches, total_matches)

                # # draw the bounding box and label on the image
                # cv2.rectangle(orig, (startX, startY), (endX, endY),
                #               (0, 255, 0), 2)
                # y = startY - 15 if startY - 15 > 15 else startY + 15
                # text = "{}: {:.2f}%".format(label, r.score * 100)
                # cv2.putText(orig, text, (startX, y),
                #             cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # cv2.imwrite("filename", orig)
