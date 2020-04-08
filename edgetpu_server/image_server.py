import io
import logging
from threading import Lock

import flask
from flask import Response, send_file

_LOGGER = logging.getLogger(__name__)


class ImageResource:
    lock = None
    image_name = None
    image_data = None

    def __init__(self, image_name, image_data=None):
        self.image_name = image_name + ".jpeg"
        self.image_data = image_data or None
        self.lock = Lock()


def get_app():
    app = flask.Flask(__name__)

    setattr(app, 'images', {})

    def set_image_data(image_res):
        if image_res.image_name in app.images:
            image_res.lock.acquire()
            try:
                image_res.image_data = image_res.image_data
            finally:
                image_res.lock.release()
        else:
            app.images[image_res.image_name] = image_res

    setattr(app, 'set_image_data', _set_image_data)

    @app.route('/image/<string:name>', methods=['GET'])
    def get_image(name):
        image = app.images.get(name, None)
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
