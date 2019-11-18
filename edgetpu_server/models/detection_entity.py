from itertools import groupby
import logging

_LOGGER = logging.getLogger(__name__)

ATTR_MATCHES = "matches"
ATTR_SUMMARY = "summary"
ATTR_TOTAL_MATCHES = "total_matches"
ATTR_SCORE = "score"
ATTR_BOX = "box"

KEY_STATE = "state"
KEY_ATTRIBUTES = "attributes"


class DetectionEntity:
    """Data structure for holding detection an entity's state."""

    def __init__(self, entity_id, labeled_detection_candidates):
        self.entity_id = entity_id
        _LOGGER.warning("Candidates %s %d",
                        str(labeled_detection_candidates),
                        len(labeled_detection_candidates))
        self.total_count = len(labeled_detection_candidates),
        self.object_detection_map = {
            label: [DetectionEntity._get_detection_entry(candidate) for candidate in list(group)]
            for label, group in groupby(labeled_detection_candidates, key=lambda x: x.label)
        }

        _LOGGER.warning("Map %s",
                        str(self.object_detection_map))

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
                    label: len(entries) for label, entries in self.object_detection_map.items()
                }
            }
        }
