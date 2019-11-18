from itertools import groupby

ATTR_MATCHES = "matches"
ATTR_SUMMARY = "summary"
ATTR_TOTAL_MATCHES = "total_matches"
ATTR_SCORE = "score"
ATTR_BOX = "box"

KEY_STATE = "state"
KEY_ATTRIBUTES = "attributes"


class DetectionEntry(dict):
    """Data structure for holding object detection information."""

    def __init__(self, labeled_detection_candidate):
        dict.__init__(self)
        self[ATTR_SCORE] = labeled_detection_candidate.percent_score
        self.box = labeled_detection_candidate.coordinate_list


class DetectionEntity:
    """Data structure for holding detection an entity's state."""

    __slots__ = ['entity_id', 'total_count', 'object_detection_map']

    def __init__(self, entity_id, labeled_detection_candidates):
        self.entity_id = entity_id
        self.total_count = len(labeled_detection_candidates),
        self.object_detection_map = {
            label: [DetectionEntity._get_detection_entry(candidate) for candidate in group]
            for label, group in groupby(labeled_detection_candidates, key=lambda x: x.label)
        }

    @staticmethod
    def _get_detection_entry(candidate):
        return {
            ATTR_SCORE: candidate.percent_score,
            ATTR_BOX: candidate.coordinate_list
        }

    def as_api_payload(self):
        return {
            KEY_STATE: self.total_count,
            KEY_ATTRIBUTES: {
                ATTR_MATCHES: self.object_detection_map,
                ATTR_TOTAL_MATCHES: self.total_count,
                ATTR_SUMMARY: {
                    len(entries) for label, entries in self.object_detection_map.items()
                }
            }
        }
