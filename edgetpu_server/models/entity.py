from itertools import groupby
from typing import List

from edgetpu_server.models.classification import Classification
from edgetpu_server.models.classification_configuration import ClassificationConfiguration


class Entity:
    """Entity configuration definition."""

    _classifications: List[Classification] = []

    def __init__(
            self,
            name: str,
            entity_id: str,
            stream_url: str,
            classification_config: ClassificationConfiguration
    ):
        """Initialize a new classification definition."""
        self._name = name
        self._entity_id = entity_id
        self._stream_url = stream_url
        self._classification_config = classification_config

    @property
    def name(self) -> str:
        """Name of the classification entity."""
        return self._name

    @property
    def entity_id(self) -> str:
        """Entity id of the classification entity."""
        return self._entity_id

    @property
    def stream_url(self) -> str:
        """Url of the video stream to process."""
        return self._stream_url

    @property
    def classification_config(self) -> ClassificationConfiguration:
        """The classification configuration for this entity."""
        return self._classification_config

    @property.setter
    def classifications(self, classifications):
        """Set the classifications that match this entity's configuration."""
        self._classifications = classifications

    @property
    def state(self) -> dict:
        """The Home-Assistant state."""
        return {
            "state": len(self._classifications),
            "attributes": {
                "matches": self._classifications_by_label,
                "total_matches": len(self._classifications),
                "summary": {
                    "label": len([]) for x, y in self._classifications
                }
            }
        }

    @property
    def _classifications_by_label(self) -> dict:
        return {
            label: [
                {
                    "score": classification.confidence,
                    "box": classification.bounding_box.coordinate_list,
                } for classification in group
            ] for label, group in groupby(
                self._classifications,
                key=lambda x: x.label,
            )
        }
