from typing import List

from edgetpu_server.models.classification_model import ClassificationConfiguration


class EntityConfiguration(object):
    """Entity configuration definition."""

    def __init__(
            self,
            name: str,
            entity_id: str,
            stream_url: str,
            min_confidence: int,
            classification_config: ClassificationConfiguration
    ):
        """Initialize a new classification definition."""
        self._name = name
        self._entity_id = entity_id
        self._stream_url = stream_url
        self._min_confidence = min_confidence
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
    def min_confidence(self) -> int:
        """Minimum confidence to consider a match."""
        return self._min_confidence

    @property
    def classification_config(self) -> ClassificationConfiguration:
        """The classification configuration for this entity."""
        return self._classification_config
