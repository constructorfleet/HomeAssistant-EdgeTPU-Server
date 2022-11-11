from typing import Tuple, List

from edgetpu_server.utils import flatten


class MatchCoordinates:
    """Cartesian coordinates for a match."""

    def __init__(
            self,
            x1: int,
            y1: int,
            x2: int,
            y2: int,
    ):
        """Initialize a new coordinate data structure."""
        self._coordinates = [
            (x1, y1),
            (x2, y2)
        ]

    @property
    def coordinates(self) -> List[Tuple[int, int]]:
        """Get the pair of coordinates that constitute this match."""
        return self._coordinates

    @property
    def coordinate_list(self) -> List[int]:
        """Get the coordinates as a flat array."""
        return flatten(self._coordinates)


class MatchLabel:
    """Label metadata."""

    def __init__(
            self,
            label: str,
            index: int,
    ):
        """Initialize a new label data structure."""
        self._label = label
        self._index = index

    @property
    def label(self):
        """The label."""
        return self._label

    @property
    def id(self):
        """The label identifier."""
        return self._index


class MatchedClassification:
    """Labeled match with bounding box."""

    def __init__(
            self,
            label: MatchLabel,
            coordinates: MatchCoordinates,
            score: int,

    ):
        """Initialize a new data structure."""
        self._label = label
        self._coordinates = coordinates
        self._score = score

    @property
    def label(self):
        """Get the label for this matched classification."""
        return self._label

    @property
    def bounding_box(self):
        """Get the coordinates of the matched classification."""
        return self._coordinates

    @property
    def confidence(self):
        """Get the confidence of the match."""
        return self._score
