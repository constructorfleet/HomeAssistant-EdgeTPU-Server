"""Modified EdgeTPU classes for ease of use."""
import logging
from typing import List

from PIL import Image
from edgetpu.detection.engine import DetectionEngine  # pylint: disable=import-error

from edgetpu_server.models.classification import Classification
from edgetpu_server.models.classification_configuration import ClassificationConfiguration

_LOGGER = logging.getLogger(__name__)


class DetectionFactory:
    """Performs detections for a given model using the EdgeTPU Engine."""

    _engines = {}

    def __init__(
            self,
            device_path: str
    ):
        """Initialize the factory."""
        self._device_path = device_path

    def process(
            self,
            frame: Image,
            config: ClassificationConfiguration
    ) -> List[Classification]:
        """Perform object detection on the given frame."""
        detections = self._get_engine(
            config.model.model_file
        ).detect_with_image(
            frame,
            config.threshold / 100,
            keep_aspect_ratio=True,
            relative_coord=False
        )

        return [
            Classification(
                label_id=candidate.label_id,
                coordinates=candidate.bounding_box.flatten(),
                score=candidate.score * 100,
            )
            for candidate
            in detections
            if (
                    candidate.label_id in config.model.model_label_ids
                    and candidate.score * 100 >= config.threshold
            )
        ]

    def _get_engine(
            self,
            model: str
    ) -> DetectionEngine:
        return self._engines.setdefault(
            model,
            DetectionEngine(model, self._device_path)
        )
