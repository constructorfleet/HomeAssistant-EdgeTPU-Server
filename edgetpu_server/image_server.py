import io
import logging
from threading import Lock

import flask
from flask import Response, send_file

_LOGGER = logging.getLogger(__name__)

images = {}


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


def get_app():
    app = flask.Flask(__name__)

    @app.route('/image', methods=['GET'])
    def get_image():
        name = (images.keys() or ['UNKNOWN'])[0]
        _LOGGER.warning('Images: {}'.format(str(list(images.keys()))))
        image = images.get(name, None)
        if image is None:
            return Response(status=404, response="%s is not found" % name)
        image.lock.acquire()
        try:
            image_data = image.image_data
        finally:
            image.lock.release()
        return send_file(
            io.BytesIO(image_data),
            attachment_filename=image.image_name,
            as_attachment=True)

    return app
