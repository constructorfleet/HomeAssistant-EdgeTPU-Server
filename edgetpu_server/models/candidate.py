"""Detection candidate with applied label."""
from edgetpu.detection.engine import DetectionCandidate


class LabeledDetectionCandidate(DetectionCandidate):
    """Data structure to hold a labeled detection candidate."""

    def __init__(self, label, detection_candidate):
        DetectionCandidate.__init__(
            self,
            label_id=detection_candidate.label_id,
            score=detection_candidate.score,
            x1=detection_candidate.x1,
            y1=detection_candidate.y1,
            x2=detection_candidate.x2,
            y2=detection_candidate.y2
        )
        self.label = label

    @property
    def coordinate_list(self):
        """Get the bounding box as a list of coordinates."""
        return self.bounding_box.flatten().tolist()

    @property
    def percent_score(self):
        """Get the detection score as a percent."""
        return self.score * 100
