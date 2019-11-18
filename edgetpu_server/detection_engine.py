"""Modified EdgeTPU classes for ease of use."""
from edgetpu.detection.engine import DetectionEngine

from edgetpu_server.models.candidate import LabeledDetectionCandidate


# pylint: disable=too-few-public-methods
class DetectionFilter:
    """Detection filter data."""

    def __init__(self, threshold, labels, labels_to_report):
        self.threshold = threshold
        self.labels = labels
        self.labels_to_report = labels_to_report

    def filter_candidates(self, candidates):
        """Filter the detection engine results."""
        filtered_candidates = []
        for result in candidates:
            label = self.labels.get(result.label_id, None)
            if not label or label not in self.labels_to_report:
                continue
            filtered_candidates.append(LabeledDetectionCandidate(label, result))

        return filtered_candidates


class FilteredDetectionEngine(DetectionEngine):
    """Detection engine that filters detected objects."""

    def __init__(
            self,
            detection_filter,
            model_path,
            device_path=None):
        """
        Args:
          model_path (str): Path to a TensorFlow Lite (``.tflite``) file.
            This model must be `compiled for the Edge TPU
            <https://coral.withgoogle.com/docs/edgetpu/compiler/>`_; otherwise, it simply executes
            on the host CPU.
          device_path (str): The device path for the Edge TPU this engine should use. This argument
            is needed only when you have multiple Edge TPUs and more inference engines than
            available Edge TPUs. For details, read `how to use multiple Edge TPUs
            <https://coral.withgoogle.com/docs/edgetpu/multiple-edgetpu/>`_.

        Raises:
          ValueError: If the model's output tensor size is not 4.
        """
        DetectionEngine.__init__(self, model_path, device_path)
        self._filter = detection_filter

    def filtered_detect_with_image(self, image):
        """Perform object detection on an image and passed through the filter criteria."""
        return self._filter.filter_candidates(
            self.DetectWithImage(
                image,
                threshold=self._filter.threshold / 100,
                keep_aspect_ratio=True,
                relative_coord=False
            )
        )
