"""Detection candidate with applied label."""
# pylint: disable=import-errror
from edgetpu.detection.engine import DetectionCandidate


class LabeledDetectionCandidate(DetectionCandidate):
    """Data structure to hold a labeled detection candidate."""

    def __init__(self, label, detection_candidate):
        box = detection_candidate.bounding_box.flatten().tolist()
        DetectionCandidate.__init__(
            self,
            label_id=detection_candidate.label_id,
            score=detection_candidate.score,
            x1=box[0],
            y1=box[1],
            x2=box[2],
            y2=box[3]
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
