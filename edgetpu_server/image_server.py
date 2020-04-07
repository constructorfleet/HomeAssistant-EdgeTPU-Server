import io
from threading import Lock

import flask
from flask import abort, Response, send_file

images = {}
app = flask.Flask(__name__)


class ImageResource:
    lock = None
    image_name = None
    image_data = None

    def __init__(self, image_name, image_data=None):
        self.image_name = image_name + ".jpeg"
        self.image_data = image_data or None
        self.lock = Lock()

    def set_image_data(self, image_data):
        self.lock.acquire()
        try:
            self.image_data = image_data
        finally:
            self.lock.release()


@app.route('/image/<string:name>', methods=['GET'])
def get_image(name):
    image = images.get(name, None)
    if image is None:
        return Response(status=404, response="%s is not found" % name)
    image.lock.acquire()
    try:
        image_data = image.image_data
    finally:
        image.lock.release()
    return send_file(
        image_data,
        attachment_filename=image.image_name,
        mimetype='image/jpg')



