import threading
import time

import cv2
import flask
import imutils
from PIL import Image
from edgetpu.detection.engine import DetectionEngine
# initialize our Flask application and the Keras model
from flask import send_file

app = flask.Flask(__name__)
engine = None
labels = None

DECIMALS = 2  # The number of decimal places data is returned to

MODEL = "/Users/tglenn/src/python/coral-pi-rest-server/models/mobilenet_ssd_v2_coco_quant_postprocess_edgetpu.tflite"
LABEL_FILE = "/Users/tglenn/src/python/coral-pi-rest-server/models/coco_labels.txt"


# Function to read labels from text files.
def read_label_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        ret = {}
        for line in lines:
            pair = line.strip().split(maxsplit=1)
            ret[int(pair[0])] = pair[1].strip()
    return ret


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


# initialize the labels dictionary
labels = None
model = None
vs = None

filename = "snapshot.jpg"


def detect():
    # loop over the frames from the video stream
    while True:
        # grab the frame from the threaded video stream and resize it
        # to have a maximum width of 500 pixels
        ret, frame = vs.read()
        frame = imutils.resize(frame, width=500)
        orig = frame.copy()

        # prepare the frame for object detection by converting (1) it
        # from BGR to RGB channel ordering and then (2) from a NumPy
        # array to PIL image format
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = Image.fromarray(frame)

        # make predictions on the input frame
        start = time.time()
        results = model.DetectWithImage(frame, threshold=args["confidence"],
                                        keep_aspect_ratio=True, relative_coord=False)
        end = time.time()

        # loop over the results
        for r in results:
            # extract the bounding box and box and predicted class label
            box = r.bounding_box.flatten().astype("int")
            (startX, startY, endX, endY) = box
            label = labels[r.label_id]

            # draw the bounding box and label on the image
            cv2.rectangle(orig, (startX, startY), (endX, endY),
                          (0, 255, 0), 2)
            y = startY - 15 if startY - 15 > 15 else startY + 15
            text = "{}: {:.2f}%".format(label, r.score * 100)
            cv2.putText(orig, text, (startX, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        cv2.imwrite("filename", orig)


def load_model(model_file=None, label_file=None):
    """
    Load model and labels.
    """
    if not model_file:
        model_file = MODEL
    if not label_file:
        label_file = LABEL_FILE

    engine = DetectionEngine(model_file)
    print("\n Loaded engine with model : {}".format(model_file))

    labels = read_label_file(label_file)
    print("\n Loaded labels from file : {}".format(label_file))


@app.route("/")
def info():
    info_str = "Flask app exposing tensorflow models via Google Coral.\n"
    return info_str


@app.route('/get_image', methods=["GET"])
def get_image():
    return send_file(filename, mimetype='image/gif')


# @app.route("/predict", methods=["POST"])
# def predict():
#     data = {"success": False}
#
#     # ensure an image was properly uploaded to our endpoint
#     if flask.request.method == "POST":
#         if flask.request.files.get("image"):
#             # read the image in PIL format
#             image_file = flask.request.files["image"]
#             print(image_file)
#             image_bytes = image_file.read()
#             image = Image.open(io.BytesIO(image_bytes))  # PIL img object.
#
#             # Run inference.
#             predictions = engine.DetectWithImage(
#                 image,
#                 threshold=0.05,
#                 keep_aspect_ratio=True,
#                 relative_coord=False,  # True = relative coordinates 0-1 of original image.
#                 top_k=10,
#             )
#
#             if predictions:
#                 data["success"] = True
#                 preds = []
#                 for prediction in predictions:
#                     bounding_box = {
#                         "x1": round(prediction.bounding_box[0, 0], DECIMALS),
#                         "x2": round(prediction.bounding_box[1, 0], DECIMALS),
#                         "y1": round(prediction.bounding_box[0, 1], DECIMALS),
#                         "y2": round(prediction.bounding_box[1, 1], DECIMALS),
#                     }
#                     preds.append(
#                         {
#                             "confidence": str(
#                                 round(100 * prediction.score, DECIMALS)
#                             ),  # A percentage.
#                             "label": labels[prediction.label_id],
#                             "bounding_box": bounding_box,
#                         }
#                     )
#                 data["predictions"] = preds
#
#     # return the data dictionary as a JSON response
#     return flask.jsonify(data)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Google Coral edgetpu flask daemon")
    parser.add_argument("--quiet", "-q", action='store_true',
                        help="log only warnings, errors")
    parser.add_argument("--port", '-p', default=5000,
                        type=int, choices=range(0, 65536),
                        help="port number")
    parser.add_argument("-m", "--model", required=True,
                        help="path to TensorFlow Lite object detection model")
    parser.add_argument("-l", "--labels", required=True,
                        help="path to labels file")
    parser.add_argument("-c", "--confidence", type=float, default=0.3,
                        help="minimum probability to filter weak detections")
    args = parser.parse_args()

    # loop over the class labels file
    for row in open(args["labels"]):
        # unpack the row and update the labels dictionary
        (classID, label) = row.strip().split(maxsplit=1)
        labels[int(classID)] = label.strip()

    model = DetectionEngine(args["model"])

    vs = cv2.VideoCapture("rtsp://10.0.50.117:7447/5c44c565e4b0b1adf6614d97_0")
    time.sleep(2.0)

    thread = threading.Thread(target=detect, args=())
    thread.daemon = True
    thread.start()

    app.run(host="0.0.0.0", port=args.port)
