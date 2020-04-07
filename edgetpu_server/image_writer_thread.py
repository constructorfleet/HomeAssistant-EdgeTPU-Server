import io
import logging

from PIL import Image, ImageDraw
from edgetpu_server.image_server import images, ImageResource

_LOGGING = logging.getLogger(__name__)


def draw_box(
    draw,
    box,
    img_width,
    img_height,
    text="",
    color=(255, 255, 0),
) -> None:
    """
    Draw a bounding box on and image.
    The bounding box is defined by the tuple (y_min, x_min, y_max, x_max)
    where the coordinates are floats in the range [0.0, 1.0] and
    relative to the width and height of the image.
    For example, if an image is 100 x 200 pixels (height x width) and the bounding
    box is `(0.1, 0.2, 0.5, 0.9)`, the upper-left and bottom-right coordinates of
    the bounding box will be `(40, 10)` to `(180, 50)` (in (x,y) coordinates).
    """

    line_width = 3
    font_height = 8
    y_min, x_min, y_max, x_max = box
    (left, right, top, bottom) = (
        x_min * img_width,
        x_max * img_width,
        y_min * img_height,
        y_max * img_height,
    )
    draw.line(
        [(left, top), (left, bottom), (right, bottom), (right, top), (left, top)],
        width=line_width,
        fill=color,
    )
    if text:
        draw.text(
            (left + line_width, abs(top - line_width - font_height)), text, fill=color
        )


class ImageWriterThread:

    def __init__(self, frame, detection_entity):
        self._frame = frame
        self._detection_entity = detection_entity

    def run(self):
        img_name = self._detection_entity.stream_name
        img = Image.open(io.BytesIO(bytearray(self._frame))).convert("RGB")
        img_width, img_height = img.size
        draw = ImageDraw.Draw(img)

        for category, values in self._detection_entity.object_detection_map.items():
            # Draw detected objects
            for instance in values:
                label = "{} {:.1f}%".format(category, instance["score"])
                draw_box(
                    draw, instance["box"], img_width, img_height, label, (255, 255, 0)
                )
        image_bytes = io.BytesIO()
        img.save(image_bytes, format='jpg')
        if img_name not in images:
            images[img_name] = ImageResource(img_name, image_bytes)
        else:
            images[img_name].set_image_data(image_bytes)

