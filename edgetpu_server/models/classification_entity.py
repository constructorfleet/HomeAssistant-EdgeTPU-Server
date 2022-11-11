from typing import List


class ClassificationEntity(object):
    """Entity classification definition."""

    def __init__(
            self,
            name: str,
            entity_id: str,
            stream_url: str,
            min_confidence: int,
            model: str,
            labels: List[str]
    ):
        """Initialize a new classification definition."""
        self._name = name
        self._entity_id = entity_id
        self._stream_url = stream_url
        self._min_confidence = min_confidence
        self._model = model
        self._labels = labels

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
    def model(self) -> str:
        """Filename of the detection model for classification."""
        return self._model

    @property
    def labels(self) -> List[str]:
        """List of labels to classify."""
        return self._labels
