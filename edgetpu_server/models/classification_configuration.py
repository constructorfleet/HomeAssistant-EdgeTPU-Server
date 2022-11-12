from typing import List


class ClassificationModel:
    """Configuration properties for classification model."""

    def __init__(
            self,
            model: str,
            label_ids: List[int]
    ):
        """Initialize a new instance of this configuration."""
        self._model_file = model
        self._model_label_ids = label_ids

    @property
    def model_file(self) -> str:
        """The TFLite model file."""
        return self._model_file

    @property
    def model_label_ids(self) -> List[int]:
        """The labels associated with the TFLite model."""
        return self._model_label_ids


class ClassificationConfiguration:
    """Configuration for a given classification."""

    def __init__(
            self,
            model: ClassificationModel,
            minimum_confidence: int,
    ):
        """Initialize a new instance of this configuration."""
        self._model = model
        self._confidence_threshold = minimum_confidence

    @property
    def model(self) -> ClassificationModel:
        """Classification model data."""
        return self._model

    @property
    def threshold(self) -> int:
        """Confidence threshold."""
        return self._confidence_threshold
