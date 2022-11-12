from edgetpu_server.models.classification_model import ClassificationModel


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
